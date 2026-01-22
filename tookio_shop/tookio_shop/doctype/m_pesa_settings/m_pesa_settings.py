# Copyright (c) 2026, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class MPesaSettings(Document):
    """
    Multi-tenant M-Pesa Settings for each seller's shop.
    Each seller inputs their own Daraja API credentials.
    """

    def before_save(self):
        """Generate callback URLs before saving"""
        self.generate_callback_urls()

    def generate_callback_urls(self):
        """Auto-generate the callback URLs for this shop"""
        base_url = frappe.utils.get_url()
        shop_id = self.shop

        # STK Push callback
        self.callback_url = f"{base_url}/api/method/tookio_shop.api.mpesa.stk_callback?shop={shop_id}"

        # C2B URLs
        self.validation_url = f"{base_url}/api/method/tookio_shop.api.mpesa.c2b_validation?shop={shop_id}"
        self.confirmation_url = f"{base_url}/api/method/tookio_shop.api.mpesa.c2b_confirmation?shop={shop_id}"

    def get_access_token(self):
        """
        Get or refresh the Daraja access token.
        Tokens are cached and refreshed when expired.
        """
        import requests
        import base64

        # Check if we have a valid cached token
        if self.access_token and self.token_expiry:
            if now_datetime() < self.token_expiry:
                return self.get_password("access_token")

        # Generate new token
        consumer_key = self.get_password("consumer_key")
        consumer_secret = self.get_password("consumer_secret")

        if not consumer_key or not consumer_secret:
            frappe.throw("M-Pesa Consumer Key and Secret are required")

        # Base64 encode credentials
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode()

        # API endpoint based on environment
        if self.environment == "Sandbox":
            url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        else:
            url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        headers = {"Authorization": f"Basic {credentials}"}

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Cache the token (expires in ~3599 seconds, we use 3500 for safety)
            self.db_set("access_token", result["access_token"])
            self.db_set("token_expiry", add_to_date(now_datetime(), seconds=3500))
            self.db_set("last_sync", now_datetime())

            frappe.logger().info(f"M-Pesa token refreshed for shop {self.shop}")
            return result["access_token"]

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"M-Pesa token error for {self.shop}: {str(e)}", "M-Pesa Token Error")
            frappe.throw(f"Failed to connect to M-Pesa: {str(e)}")

    def initiate_stk_push(self, phone_number, amount, account_reference, description=None):
        """
        Initiate STK Push (Lipa Na M-Pesa Online) request.
        
        Args:
            phone_number: Customer phone (254XXXXXXXXX format)
            amount: Amount to charge
            account_reference: Order/Invoice reference
            description: Transaction description
        
        Returns:
            dict with CheckoutRequestID and success status
        """
        import requests
        import base64
        from datetime import datetime

        if not self.enabled:
            frappe.throw("M-Pesa is not enabled for this shop")

        token = self.get_access_token()
        passkey = self.get_password("passkey")

        if not passkey:
            frappe.throw("M-Pesa Passkey is required for STK Push")

        # Generate timestamp and password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{self.shortcode}{passkey}{timestamp}".encode()
        ).decode()

        # Normalize phone number to 254 format
        phone = self.normalize_phone(phone_number)

        # API endpoint
        if self.environment == "Sandbox":
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        else:
            url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline" if self.business_type == "Paybill" else "CustomerBuyGoodsOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference[:12],  # Max 12 chars
            "TransactionDesc": (description or f"Payment for {account_reference}")[:13]  # Max 13 chars
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            result = response.json()

            if result.get("ResponseCode") == "0":
                # Log the transaction
                self.log_transaction(
                    checkout_request_id=result.get("CheckoutRequestID"),
                    merchant_request_id=result.get("MerchantRequestID"),
                    phone_number=phone,
                    amount=amount,
                    account_reference=account_reference,
                    status="Initiated"
                )
                return {
                    "success": True,
                    "checkout_request_id": result.get("CheckoutRequestID"),
                    "merchant_request_id": result.get("MerchantRequestID"),
                    "message": "STK Push sent. Check your phone."
                }
            else:
                frappe.log_error(f"STK Push failed: {result}", "M-Pesa STK Error")
                return {
                    "success": False,
                    "error": result.get("errorMessage", "Failed to initiate payment")
                }

        except requests.exceptions.RequestException as e:
            frappe.log_error(f"STK Push error: {str(e)}", "M-Pesa STK Error")
            frappe.throw(f"Payment request failed: {str(e)}")

    def log_transaction(self, **kwargs):
        """Create a M-Pesa Transaction log"""
        doc = frappe.new_doc("M-Pesa Transaction")
        doc.shop = self.shop
        doc.update(kwargs)
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc.name

    @staticmethod
    def normalize_phone(phone):
        """Convert phone to 254XXXXXXXXX format"""
        phone = str(phone).strip().replace(" ", "").replace("-", "")
        
        if phone.startswith("+"):
            phone = phone[1:]
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        if not phone.startswith("254"):
            phone = "254" + phone
            
        return phone


def get_mpesa_settings_for_shop(shop):
    """Helper to get M-Pesa settings for a specific shop"""
    settings_name = frappe.db.get_value(
        "M-Pesa Settings",
        {"shop": shop, "enabled": 1},
        "name"
    )
    if settings_name:
        return frappe.get_doc("M-Pesa Settings", settings_name)
    return None
