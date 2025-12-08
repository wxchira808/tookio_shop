"""
Pesapal Payment Gateway Integration for Tookio Shop
"""

import frappe
import requests
from datetime import datetime
import json

# Pesapal API endpoints
PESAPAL_SANDBOX_URL = "https://cybqa.pesapal.com/pesapalv3"
PESAPAL_LIVE_URL = "https://pay.pesapal.com/v3"

# COMMENTED OUT - Making app FREE
# @frappe.whitelist()
# def initiate_pesapal_payment(phone_number, amount, plan_name):
#     """Initiate Pesapal payment for subscription"""
#     try:
#         # Get Pesapal settings
#         settings = get_pesapal_settings()
#         if not settings:
#             frappe.throw("Pesapal not configured. Please contact support.")

#         # Get access token
#         token = get_pesapal_token(settings)

#         # Prepare order data
#         order_data = {
#             "id": f"SUB-{frappe.session.user}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
#             "currency": "KES",
#             "amount": float(amount),
#             "description": f"Tookio Shop Subscription - {plan_name}",
#             "callback_url": f"{frappe.utils.get_url()}/api/method/tookio_shop.api.pesapal_callback",
#             "notification_id": settings.notification_id or "",
#             "billing_address": {
#                 "phone_number": phone_number,
#                 "email_address": frappe.session.user,
#                 "country_code": "KE",
#                 "first_name": "Tookio",
#                 "last_name": "User"
#             }
#         }

#         # Submit order request
#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }

#         base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
#         response = requests.post(
            f"{base_url}/api/Transactions/SubmitOrderRequest",
            headers=headers,
            json=order_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            # Log payment
            log_payment(order_data, result, "initiated")

            return {
                "redirect_url": result.get("redirect_url"),
                "order_tracking_id": result.get("order_tracking_id")
            }
        else:
            error_msg = f"Pesapal API error: {response.status_code} - {response.text}"
            frappe.log_error(error_msg, "Pesapal Payment Initiation")
            frappe.throw("Failed to initiate payment. Please try again.")

    except Exception as e:
        frappe.log_error(str(e), "Pesapal Payment Initiation")
        frappe.throw("Failed to initiate Pesapal payment. Please try again.")

# COMMENTED OUT - Making app FREE
# @frappe.whitelist(allow_guest=True)
# def pesapal_callback():
    """Handle Pesapal IPN callback"""
    try:
        data = frappe.form_dict

        order_tracking_id = data.get("OrderTrackingId")
        if not order_tracking_id:
            frappe.log_error("No OrderTrackingId in callback", "Pesapal Callback")
            return {"status": "error", "message": "Missing OrderTrackingId"}

        # Get payment log
        payment_log = frappe.get_doc("Pesapal Payment Log", {"order_tracking_id": order_tracking_id})
        if not payment_log:
            frappe.log_error(f"Payment log not found for {order_tracking_id}", "Pesapal Callback")
            return {"status": "error", "message": "Payment log not found"}

        # Get payment status from Pesapal
        settings = get_pesapal_settings()
        token = get_pesapal_token(settings)

        base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            status_data = response.json()

            # Update payment log
            payment_log.status = "Completed" if status_data.get("payment_status_description") == "Completed" else "Failed"
            payment_log.transaction_id = status_data.get("confirmation_code") or ""
            payment_log.raw_response = json.dumps(status_data)
            payment_log.save(ignore_permissions=True)

            # If completed, activate subscription
            if payment_log.status == "Completed":
                activate_subscription_for_user(payment_log.customer, payment_log.transaction_id)

            frappe.logger().info(f"Pesapal payment {payment_log.status} for {order_tracking_id}")
            return {"status": "success"}

        else:
            frappe.log_error(f"Failed to get payment status: {response.text}", "Pesapal Callback")
            return {"status": "error", "message": "Failed to verify payment"}

    except Exception as e:
        frappe.log_error(str(e), "Pesapal Callback")
        return {"status": "error", "message": str(e)}

# COMMENTED OUT - Making app FREE
# @frappe.whitelist()
# def verify_pesapal_payment(order_tracking_id):
    """Verify Pesapal payment status"""
    try:
        settings = get_pesapal_settings()
        token = get_pesapal_token(settings)

        base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            status_data = response.json()
            return {
                "status": status_data.get("payment_status_description"),
                "transaction_id": status_data.get("confirmation_code"),
                "amount": status_data.get("amount"),
                "currency": status_data.get("currency")
            }
        else:
            frappe.throw("Failed to verify payment status")

    except Exception as e:
        frappe.log_error(str(e), "Pesapal Payment Verification")
        frappe.throw("Failed to verify payment")

# COMMENTED OUT - Making app FREE
# @frappe.whitelist()
# def register_pesapal_ipn():
    """Register IPN URL with Pesapal"""
    try:
        settings = get_pesapal_settings()
        token = get_pesapal_token(settings)

        callback_url = f"{frappe.utils.get_url()}/api/method/tookio_shop.api.pesapal_callback"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "url": callback_url,
            "ipn_notification_type": "POST"
        }

        base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
        response = requests.post(
            f"{base_url}/api/URLSetup/RegisterIPN",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            ipn_data = response.json()
            settings.notification_id = ipn_data.get("ipn_id")
            settings.save()
            return {"success": True, "ipn_id": ipn_data.get("ipn_id")}
        else:
            frappe.throw(f"Failed to register IPN: {response.text}")

    except Exception as e:
        frappe.log_error(str(e), "Pesapal IPN Registration")
        frappe.throw("Failed to register IPN URL")

def get_pesapal_token(settings):
    """Get Pesapal access token"""
    try:
        headers = {"Content-Type": "application/json"}

        data = {
            "consumer_key": settings.get_password("consumer_key"),
            "consumer_secret": settings.get_password("consumer_secret")
        }

        base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
        response = requests.post(
            f"{base_url}/api/Auth/RequestToken",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("token")
        else:
            frappe.throw(f"Failed to get Pesapal token: {response.text}")

    except Exception as e:
        frappe.log_error(str(e), "Pesapal Token Generation")
        raise

def get_pesapal_settings():
	"""Get Pesapal settings"""
	try:
		return frappe.get_single("Pesapal Gateway Setting")
	except:
		return None
def log_payment(order_data, response_data, status):
    """Log payment transaction"""
    try:
        log = frappe.get_doc({
            "doctype": "Pesapal Payment Log",
            "reference": order_data["id"],
            "order_tracking_id": response_data.get("order_tracking_id"),
            "amount": order_data["amount"],
            "currency": order_data["currency"],
            "status": status,
            "customer": frappe.session.user,
            "payment_method": "Pesapal",
            "raw_response": json.dumps(response_data)
        })
        log.insert(ignore_permissions=True)
        frappe.logger().info(f"Pesapal payment logged: {order_data['id']}")
    except Exception as e:
        frappe.log_error(str(e), "Pesapal Payment Logging")

def activate_subscription_for_user(customer, transaction_id):
    """Activate subscription for user after successful payment"""
    try:
        # This should call your existing subscription activation logic
        # For now, just log it
        frappe.logger().info(f"Activating subscription for {customer} with transaction {transaction_id}")

        # You can add your subscription activation logic here
        # For example:
        # activate_subscription(plan_name, "Pesapal", transaction_id)

    except Exception as e:
        frappe.log_error(str(e), "Subscription Activation")

# FREE APP - Stub functions for mobile app compatibility
@frappe.whitelist()
def activate_subscription(plan_name, payment_method, transaction_id):
    """Stub function - app is now free"""
    return {"success": True, "message": "Tookio Shop is FREE forever! No subscription needed."}

@frappe.whitelist()
def cancel_subscription():
    """Stub function - app is now free"""
    return {"success": True, "message": "Tookio Shop is FREE forever! No subscription to cancel."}

@frappe.whitelist()
def get_subscription_details():
    """Stub function - app is now free"""
    return {
        "plan": "FREE Forever",
        "status": "Active",
        "features": ["Unlimited items", "Unlimited shops", "All features"],
        "message": "Tookio Shop is completely FREE with no limits!"
    }