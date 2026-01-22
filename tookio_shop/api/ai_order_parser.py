"""
AI Order Parser API for Tookio Shop
The "DMs to Data" engine - converts messy customer messages into structured orders.

Examples of messages it can parse:
- "I want 2 red bags sent to Ngong"
- "Can I get the blue dress size M? Deliver to Westlands please"
- "Nafuata kikoi ya 500 na pair moja ya sandals. Nitakuwa Kitengela"
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=False)
def parse_dm(shop, message, platform="WhatsApp"):
    """
    Parse a customer DM and extract order information.
    
    Args:
        shop: Shop docname
        message: The customer's message text
        platform: Source platform (WhatsApp, Instagram, TikTok, etc.)
    
    Returns:
        dict with:
        - products: list of {name, quantity, variant}
        - customer_name: extracted customer name
        - delivery_location: delivery address
        - special_instructions: any special notes
        - confidence: AI confidence score (0-100)
        - order_created: order name if auto-created
    """
    from tookio_shop.tookio_shop.doctype.tookio_ai_agent.tookio_ai_agent import get_ai_agent_for_shop

    # Verify shop ownership
    shop_doc = frappe.get_doc("Shop", shop)
    if shop_doc.owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized for this shop"))

    # Get AI agent for this shop
    agent = get_ai_agent_for_shop(shop)
    if not agent:
        return {
            "error": "AI Agent not configured for this shop. Please set up your AI settings.",
            "configured": False
        }

    # Parse the message
    result = agent.parse_dm(message, platform)
    result["configured"] = True
    
    return result


@frappe.whitelist(allow_guest=False)
def parse_dm_batch(shop, messages):
    """
    Parse multiple DMs at once.
    
    Args:
        shop: Shop docname
        messages: List of {text, platform, customer_phone}
    
    Returns:
        List of parsed results
    """
    import json
    
    if isinstance(messages, str):
        messages = json.loads(messages)

    results = []
    for msg in messages:
        result = parse_dm(
            shop=shop,
            message=msg.get("text", ""),
            platform=msg.get("platform", "WhatsApp")
        )
        result["original_message"] = msg.get("text", "")
        result["customer_phone"] = msg.get("customer_phone", "")
        results.append(result)

    return results


@frappe.whitelist(allow_guest=False)
def create_order_from_dm(shop, message, customer_phone, platform="WhatsApp"):
    """
    Parse DM and immediately create a draft order.
    Used when seller manually triggers order creation from a DM.
    
    Args:
        shop: Shop docname
        message: Customer's message
        customer_phone: Customer's phone number
        platform: Source platform
    
    Returns:
        Order details with order name
    """
    from tookio_shop.tookio_shop.doctype.tookio_ai_agent.tookio_ai_agent import get_ai_agent_for_shop

    # Parse first
    parsed = parse_dm(shop, message, platform)
    
    if parsed.get("error"):
        return parsed

    if parsed.get("order_created"):
        # Order already auto-created
        order = frappe.get_doc("Sales Order", parsed["order_created"])
        order.customer_phone = customer_phone
        order.save()
        return {
            "success": True,
            "order": order.name,
            "message": f"Order {order.name} created from DM"
        }

    # Create order manually if not auto-created
    agent = get_ai_agent_for_shop(shop)
    
    order = frappe.new_doc("Sales Order")
    order.shop = shop
    order.order_source = "AI Parsed"
    order.dm_source_platform = platform
    order.original_dm_text = message
    order.ai_parsed = 1
    order.ai_confidence = parsed.get("confidence", 0)
    order.order_status = "Draft"
    order.payment_status = "Unpaid"
    order.customer_name = parsed.get("customer_name") or "Customer from DM"
    order.customer_phone = customer_phone
    order.delivery_location = parsed.get("delivery_location", "")
    order.delivery_notes = parsed.get("special_instructions", "")

    # Add items
    for product_data in parsed.get("products", []):
        _add_item_to_order(order, product_data, shop)

    order.flags.ignore_permissions = True
    order.insert()

    return {
        "success": True,
        "order": order.name,
        "parsed_data": parsed,
        "message": f"Draft order {order.name} created. Review and confirm."
    }


def _add_item_to_order(order, product_data, shop):
    """Helper to add an item to an order"""
    product_name = product_data.get("name", "")
    quantity = product_data.get("quantity", 1)

    # Try to find matching product
    matched_product = frappe.db.get_value(
        "Product",
        {"shop": shop, "item_name": ["like", f"%{product_name}%"], "enabled": 1},
        ["name", "item_name", "selling_price"],
        as_dict=True
    )

    order.append("items", {
        "product": matched_product.name if matched_product else None,
        "item_name": matched_product.item_name if matched_product else product_name,
        "qty": quantity,
        "rate": matched_product.selling_price if matched_product else 0,
        "amount": quantity * (matched_product.selling_price if matched_product else 0)
    })


@frappe.whitelist(allow_guest=False)
def get_ai_status(shop):
    """
    Check if AI is configured for a shop.
    Used by frontend to show setup prompts.
    """
    # Verify ownership
    shop_doc = frappe.get_doc("Shop", shop)
    if shop_doc.owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"))

    agent = frappe.db.get_value(
        "AI Agent",
        {"shop": shop},
        ["enabled", "ai_provider", "model_name", "last_product_sync"],
        as_dict=True
    )

    if not agent:
        return {
            "configured": False,
            "message": "AI not configured. Set up your AI Agent to parse DMs automatically."
        }

    return {
        "configured": True,
        "enabled": agent.enabled,
        "provider": agent.ai_provider,
        "model": agent.model_name,
        "last_sync": agent.last_product_sync
    }


@frappe.whitelist(allow_guest=False)
def sync_product_context(shop):
    """
    Manually sync product list for AI context.
    Called when seller updates their inventory.
    """
    from tookio_shop.tookio_shop.doctype.tookio_ai_agent.tookio_ai_agent import get_ai_agent_for_shop

    agent = get_ai_agent_for_shop(shop)
    if not agent:
        return {"error": "AI Agent not found"}

    agent.sync_product_list()
    agent.save()

    return {
        "success": True,
        "message": "Product context updated",
        "last_sync": str(agent.last_product_sync)
    }


@frappe.whitelist(allow_guest=False)
def test_ai_connection(shop):
    """
    Test the AI connection with a sample message.
    Used during setup to verify API key works.
    """
    from tookio_shop.tookio_shop.doctype.tookio_ai_agent.tookio_ai_agent import get_ai_agent_for_shop

    agent = get_ai_agent_for_shop(shop)
    if not agent:
        return {"success": False, "error": "AI Agent not configured"}

    test_message = "I want 2 bags and 1 dress delivered to Nairobi CBD"
    
    try:
        result = agent.parse_dm(test_message, "Test")
        
        if result.get("error"):
            return {"success": False, "error": result["error"]}

        return {
            "success": True,
            "message": "AI connection successful!",
            "test_result": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
