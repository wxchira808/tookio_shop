# Copyright (c) 2026, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import json


class AIAgent(Document):
    """
    AI Agent configuration for parsing DMs into orders.
    Each shop can have its own AI settings and API key.
    """

    def before_save(self):
        """Sync product list if enabled"""
        if self.include_product_list:
            self.sync_product_list()

    def sync_product_list(self):
        """Cache the shop's product list for AI context"""
        products = frappe.get_all(
            "Product",
            filters={"shop": self.shop, "enabled": 1},
            fields=["name", "item_name", "selling_price", "stock_quantity"]
        )

        # Format for AI context
        product_list = []
        for p in products:
            product_list.append({
                "id": p.name,
                "name": p.item_name,
                "price": p.selling_price,
                "in_stock": p.stock_quantity > 0
            })

        self.product_list_cache = json.dumps(product_list, indent=2)
        self.last_product_sync = now_datetime()

    def get_ai_client(self):
        """Get the appropriate AI client based on provider"""
        api_key = self.get_password("api_key")
        
        if not api_key:
            frappe.throw("AI API Key is required")

        if self.ai_provider == "Google Gemini":
            return GeminiClient(api_key, self.model_name, self.temperature)
        elif self.ai_provider == "OpenAI":
            return OpenAIClient(api_key, self.model_name, self.temperature)
        elif self.ai_provider == "Anthropic Claude":
            return ClaudeClient(api_key, self.model_name, self.temperature)
        else:
            frappe.throw(f"Unsupported AI provider: {self.ai_provider}")

    def parse_dm(self, dm_text, platform="WhatsApp"):
        """
        Parse a DM message using AI and optionally create an order.
        
        Args:
            dm_text: The customer's message
            platform: WhatsApp, Instagram, TikTok, etc.
        
        Returns:
            dict with parsed order data and confidence score
        """
        if not self.enabled:
            return {"error": "AI Agent is disabled for this shop"}

        # Build prompt with product context
        full_prompt = self._build_prompt(dm_text)

        # Call AI
        client = self.get_ai_client()
        try:
            response = client.complete(
                system_prompt=self.system_prompt,
                user_prompt=full_prompt,
                max_tokens=self.max_tokens
            )

            # Parse JSON response
            parsed = self._extract_json(response)
            
            if parsed.get("confidence", 0) >= self.confidence_threshold:
                # High confidence - optionally create order
                if self.auto_create_orders:
                    order = self._create_draft_order(parsed, dm_text, platform)
                    parsed["order_created"] = order.name

            return parsed

        except Exception as e:
            frappe.log_error(f"AI parsing error: {str(e)}", "AI Order Parser")
            return {"error": str(e), "confidence": 0}

    def _build_prompt(self, dm_text):
        """Build the full prompt with product context"""
        prompt = f"Customer message:\n\n{dm_text}\n\n"

        if self.include_product_list and self.product_list_cache:
            prompt += f"Available products in this shop:\n{self.product_list_cache}\n\n"

        prompt += "Parse this message and extract order information."
        return prompt

    def _extract_json(self, response_text):
        """Extract JSON from AI response"""
        import re
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # If no valid JSON, return error
        return {"error": "Could not parse AI response", "confidence": 0, "raw": response_text}

    def _create_draft_order(self, parsed_data, original_dm, platform):
        """Create a draft order from parsed DM data"""
        order = frappe.new_doc("Sales Order")
        order.shop = self.shop
        order.order_source = "AI Parsed"
        order.dm_source_platform = platform
        order.original_dm_text = original_dm
        order.ai_parsed = 1
        order.ai_confidence = parsed_data.get("confidence", 0)
        order.order_status = "Draft"
        order.payment_status = "Unpaid"

        # Customer info
        order.customer_name = parsed_data.get("customer_name") or "Customer from DM"
        order.customer_phone = ""  # Need to get from platform
        order.delivery_location = parsed_data.get("delivery_location", "")
        order.delivery_notes = parsed_data.get("special_instructions", "")

        # Add items
        for product in parsed_data.get("products", []):
            self._add_item_to_order(order, product)

        if self.require_confirmation:
            order.order_status = "Draft"  # Needs seller confirmation
        
        order.flags.ignore_permissions = True
        order.insert()

        frappe.logger().info(f"AI created draft order {order.name} from DM")
        return order

    def _add_item_to_order(self, order, product_data):
        """Match parsed product to actual inventory and add to order"""
        product_name = product_data.get("name", "")
        quantity = product_data.get("quantity", 1)

        # Try to find matching product
        matched_product = self._find_product(product_name)

        order.append("items", {
            "product": matched_product.name if matched_product else None,
            "item_name": matched_product.item_name if matched_product else product_name,
            "qty": quantity,
            "rate": matched_product.selling_price if matched_product else 0,
            "amount": quantity * (matched_product.selling_price if matched_product else 0)
        })

    def _find_product(self, product_name):
        """Find a product by fuzzy name matching"""
        # First try exact match
        product = frappe.db.get_value(
            "Product",
            {"shop": self.shop, "item_name": ["like", f"%{product_name}%"], "enabled": 1},
            ["name", "item_name", "selling_price"],
            as_dict=True
        )
        return product


# ==================== AI PROVIDER CLIENTS ====================

class GeminiClient:
    """Google Gemini API client"""
    
    def __init__(self, api_key, model, temperature):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def complete(self, system_prompt, user_prompt, max_tokens=500):
        import requests

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
            }],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": max_tokens
            }
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]


class OpenAIClient:
    """OpenAI API client"""
    
    def __init__(self, api_key, model, temperature):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def complete(self, system_prompt, user_prompt, max_tokens=500):
        import requests

        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


class ClaudeClient:
    """Anthropic Claude API client"""
    
    def __init__(self, api_key, model, temperature):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    def complete(self, system_prompt, user_prompt, max_tokens=500):
        import requests

        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]


# ==================== HELPER FUNCTIONS ====================

def get_ai_agent_for_shop(shop):
    """Get AI Agent settings for a shop"""
    agent_name = frappe.db.get_value(
        "AI Agent",
        {"shop": shop, "enabled": 1},
        "name"
    )
    if agent_name:
        return frappe.get_doc("AI Agent", agent_name)
    return None
