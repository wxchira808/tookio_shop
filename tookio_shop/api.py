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
#             f"{base_url}/api/Transactions/SubmitOrderRequest",
#             headers=headers,
#             json=order_data,
#             timeout=30
#         )

#         if response.status_code == 200:
#             result = response.json()

#             # Log payment
#             log_payment(order_data, result, "initiated")

#             return {
#                 "redirect_url": result.get("redirect_url"),
#                 "order_tracking_id": result.get("order_tracking_id")
#             }
#         else:
#             error_msg = f"Pesapal API error: {response.status_code} - {response.text}"
#             frappe.log_error(error_msg, "Pesapal Payment Initiation")
#             frappe.throw("Failed to initiate payment. Please try again.")

#     except Exception as e:
#         frappe.log_error(str(e), "Pesapal Payment Initiation")
#         frappe.throw("Failed to initiate Pesapal payment. Please try again.")

# COMMENTED OUT - Making app FREE
# @frappe.whitelist(allow_guest=True)
# def pesapal_callback():
#     """Handle Pesapal IPN callback"""
#     try:
#         data = frappe.form_dict

#         order_tracking_id = data.get("OrderTrackingId")
#         if not order_tracking_id:
#             frappe.log_error("No OrderTrackingId in callback", "Pesapal Callback")
#             return {"status": "error", "message": "Missing OrderTrackingId"}

#         # Get payment log
#         payment_log = frappe.get_doc("Pesapal Payment Log", {"order_tracking_id": order_tracking_id})
#         if not payment_log:
#             frappe.log_error(f"Payment log not found for {order_tracking_id}", "Pesapal Callback")
#             return {"status": "error", "message": "Payment log not found"}

#         # Get payment status from Pesapal
#         settings = get_pesapal_settings()
#         token = get_pesapal_token(settings)

#         base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
#         headers = {"Authorization": f"Bearer {token}"}

#         response = requests.get(
#             f"{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
#             headers=headers,
#             timeout=30
#         )

#         if response.status_code == 200:
#             status_data = response.json()

#             # Update payment log
#             payment_log.status = "Completed" if status_data.get("payment_status_description") == "Completed" else "Failed"
#             payment_log.transaction_id = status_data.get("confirmation_code") or ""
#             payment_log.raw_response = json.dumps(status_data)
#             payment_log.save(ignore_permissions=True)

#             # If completed, activate subscription
#             if payment_log.status == "Completed":
#                 activate_subscription_for_user(payment_log.customer, payment_log.transaction_id)

#             frappe.logger().info(f"Pesapal payment {payment_log.status} for {order_tracking_id}")
#             return {"status": "success"}

#         else:
#             frappe.log_error(f"Failed to get payment status: {response.text}", "Pesapal Callback")
#             return {"status": "error", "message": "Failed to verify payment"}

#     except Exception as e:
#         frappe.log_error(str(e), "Pesapal Callback")
#         return {"status": "error", "message": str(e)}

# COMMENTED OUT - Making app FREE
# @frappe.whitelist()
# def verify_pesapal_payment(order_tracking_id):
#     """Verify Pesapal payment status"""
#     try:
#         settings = get_pesapal_settings()
#         token = get_pesapal_token(settings)

#         base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
#         headers = {"Authorization": f"Bearer {token}"}

#         response = requests.get(
#             f"{base_url}/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}",
#             headers=headers,
#             timeout=30
#         )

#         if response.status_code == 200:
#             status_data = response.json()
#             return {
#                 "status": status_data.get("payment_status_description"),
#                 "transaction_id": status_data.get("confirmation_code"),
#                 "amount": status_data.get("amount"),
#                 "currency": status_data.get("currency")
#             }
#         else:
#             frappe.throw("Failed to verify payment status")

#     except Exception as e:
#         frappe.log_error(str(e), "Pesapal Payment Verification")
#         frappe.throw("Failed to verify payment")

# COMMENTED OUT - Making app FREE
# @frappe.whitelist()
# def register_pesapal_ipn():
#     """Register IPN URL with Pesapal"""
#     try:
#         settings = get_pesapal_settings()
#         token = get_pesapal_token(settings)

#         callback_url = f"{frappe.utils.get_url()}/api/method/tookio_shop.api.pesapal_callback"

#         headers = {
#             "Authorization": f"Bearer {token}",
#             "Content-Type": "application/json"
#         }

#         data = {
#             "url": callback_url,
#             "ipn_notification_type": "POST"
#         }

#         base_url = PESAPAL_SANDBOX_URL if settings.is_sandbox else PESAPAL_LIVE_URL
#         response = requests.post(
#             f"{base_url}/api/URLSetup/RegisterIPN",
#             headers=headers,
#             json=data,
#             timeout=30
#         )

#         if response.status_code == 200:
#             ipn_data = response.json()
#             settings.notification_id = ipn_data.get("ipn_id")
#             settings.save()
#             return {"success": True, "ipn_id": ipn_data.get("ipn_id")}
#         else:
#             frappe.throw(f"Failed to register IPN: {response.text}")

#     except Exception as e:
#         frappe.log_error(str(e), "Pesapal IPN Registration")
#         frappe.throw("Failed to register IPN URL")

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

# ==================== NEW SUBSCRIPTION SYSTEM ====================

@frappe.whitelist(allow_guest=False)
def get_subscription_plans():
    """Get all available subscription plans"""
    plans = frappe.get_all(
        "Tookio Subscription",
        filters={"enabled": 1},
        fields=["name", "subscription_name", "description", "price", "currency", "shop_limit", "products_limit", "sales_invoice_limit"],
        order_by="price asc"
    )
    return {"plans": plans}

@frappe.whitelist(allow_guest=False)
def get_user_subscription():
    """Get current user's subscription details"""
    from frappe.utils import today, getdate
    
    try:
        user = frappe.session.user
        
        # Get user subscription
        user_sub = frappe.db.exists("Tookio User Subscription", {"user": user})
        
        if user_sub:
            doc = frappe.get_doc("Tookio User Subscription", user_sub)
            
            # Check if subscription has expired and auto-downgrade
            try:
                if doc.subscription_end_date:
                    end_date = getdate(doc.subscription_end_date)
                    current_date = getdate(today())
                    
                    if current_date > end_date and doc.status != "Expired":
                        frappe.logger().info(f"🔄 Auto-downgrading expired subscription for {user} to Free Plan")
                        doc.status = "Expired"
                        doc.current_subscription = "Free Plan"
                        doc.subscription_start_date = current_date
                        doc.subscription_end_date = None  # Free plan never expires
                        doc.shop_limit = 1
                        doc.products_limit = 50
                        doc.sales_invoice_limit = 200
                        doc.save(ignore_permissions=True)
                        frappe.db.commit()
            except Exception as e:
                frappe.logger().error(f"❌ Error checking subscription expiry: {str(e)}")
                # Continue anyway, don't break the function
            
            # Get actual counts for current usage
            current_shops = frappe.db.count("Shop", {"owner": user})
            current_products = frappe.db.count("Product", {"owner": user})
            current_sales_invoices = frappe.db.count("Sale Invoice", {"owner": user})
            
            # Get subscription plan name
            plan_name = "Free Plan"
            if doc.current_subscription and doc.current_subscription != "Free Plan":
                try:
                    plan_doc = frappe.get_doc("Tookio Subscription", doc.current_subscription)
                    plan_name = plan_doc.subscription_name
                except:
                    plan_name = doc.current_subscription
            
            return {
                "has_subscription": doc.current_subscription and doc.current_subscription != "Free Plan",
                "subscription_plan": plan_name,
                "current_subscription": doc.current_subscription,
                "subscription_start_date": str(doc.subscription_start_date) if doc.subscription_start_date else None,
                "subscription_end_date": str(doc.subscription_end_date) if doc.subscription_end_date else None,
                "status": doc.status,
                "shop_limit": doc.shop_limit,
                "products_limit": doc.products_limit,
                "sales_invoice_limit": doc.sales_invoice_limit,
                "current_shops": current_shops,
                "current_products": current_products,
                "current_sales_invoices": current_sales_invoices,
            }
        else:
            # Return free plan as default
            current_shops = frappe.db.count("Shop", {"owner": user})
            current_products = frappe.db.count("Product", {"owner": user})
            current_sales_invoices = frappe.db.count("Sale Invoice", {"owner": user})
            
            return {
                "has_subscription": False,
                "subscription_plan": "Free Plan",
                "current_subscription": "Free Plan",
                "subscription_start_date": str(getdate(today())),
                "subscription_end_date": None,
                "status": "Active",
                "shop_limit": 1,
                "products_limit": 50,
                "sales_invoice_limit": 200,
                "current_shops": current_shops,
                "current_products": current_products,
                "current_sales_invoices": current_sales_invoices,
            }
    
    except Exception as e:
        frappe.logger().error(f"❌ Error in get_user_subscription: {str(e)}")
        # Return safe default on error
        return {
            "has_subscription": False,
            "subscription_plan": "Free Plan",
            "current_subscription": "Free Plan",
            "status": "Active",
            "shop_limit": 1,
            "products_limit": 50,
            "sales_invoice_limit": 200,
            "current_shops": 0,
            "current_products": 0,
            "current_sales_invoices": 0,
        }

@frappe.whitelist(allow_guest=False)
def submit_payment_confirmation(subscription_plan, user_name):
    """User submits that they've made payment - immediately upgrade them"""
    user = frappe.session.user
    
    # Debug logging
    frappe.logger().info(f"🔔 submit_payment_confirmation called for user: {user}, plan: {subscription_plan}")

    # Get the subscription plan details
    plan = frappe.get_doc("Tookio Subscription", subscription_plan)
    if not plan:
        frappe.throw("Invalid subscription plan")

    # Immediately upgrade the user (bypass manual verification)
    frappe.logger().info(f"🚀 Upgrading user {user} to {subscription_plan}")
    upgrade_user_subscription(user, subscription_plan)
    frappe.logger().info(f"✅ User {user} upgraded successfully")

    # Create payment confirmation record for admin records (marked as auto-verified)
    doc = frappe.new_doc("Tookio Payment Confirmation")
    doc.user = user
    doc.user_name = user_name or ""
    doc.subscription_plan = subscription_plan
    doc.till_number = "6547212"
    doc.status = "Verified"  # Auto-verified since we upgraded immediately
    doc.verified_by = "Administrator"  # Mark as auto-verified
    doc.verified_date = frappe.utils.now()
    doc.notes = "Auto-verified upgrade from mobile app"
    doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "message": "Your account has been upgraded successfully! You now have access to premium features.",
        "confirmation_id": doc.name
    }


def upgrade_user_subscription(user, subscription_plan):
    """Upgrade user subscription - extracted from TookioPaymentConfirmation.on_update"""
    frappe.logger().info(f"📝 upgrade_user_subscription called for {user} with plan {subscription_plan}")
    
    # Get the subscription plan details
    plan = frappe.get_doc("Tookio Subscription", subscription_plan)

    # Check if user already has a subscription record
    user_sub_name = frappe.db.exists("Tookio User Subscription", {"user": user})
    
    frappe.logger().info(f"💾 Existing subscription found: {user_sub_name}")

    if user_sub_name:
        # Update existing subscription
        doc = frappe.get_doc("Tookio User Subscription", user_sub_name)
        frappe.logger().info(f"📄 Updating existing subscription {user_sub_name}")
    else:
        # Create new subscription record
        doc = frappe.new_doc("Tookio User Subscription")
        doc.user = user
        frappe.logger().info(f"📄 Creating new subscription for {user}")

    # Update subscription details
    doc.current_subscription = subscription_plan
    doc.subscription_start_date = frappe.utils.getdate()
    doc.subscription_end_date = frappe.utils.add_months(frappe.utils.getdate(), 1)  # 1 month subscription
    doc.status = "Active"

    # Set limits from the plan
    doc.shop_limit = plan.shop_limit
    doc.products_limit = plan.products_limit
    doc.sales_invoice_limit = plan.sales_invoice_limit
    
    frappe.logger().info(f"💪 Set limits: shops={plan.shop_limit}, products={plan.products_limit}, invoices={plan.sales_invoice_limit}")

    # Save to trigger the hooks that populate limits and history
    doc.save(ignore_permissions=True)
    
    frappe.logger().info(f"✅ Subscription saved successfully for {user}")

    frappe.db.commit()
    
    frappe.logger().info(f"🎉 Database committed - upgrade complete for {user}")

@frappe.whitelist(allow_guest=False)
def check_user_limits():
    """Check if user has exceeded their subscription limits"""
    try:
        user = frappe.session.user
        
        # Get user subscription limits
        user_sub_data = get_user_subscription()
        shop_limit = user_sub_data.get("shop_limit", 1)
        products_limit = user_sub_data.get("products_limit", 50)
        sales_invoice_limit = user_sub_data.get("sales_invoice_limit", 200)
        
        # Count current usage
        shops_count = frappe.db.count("Shop", {"owner": user})
        products_count = frappe.db.count("Product", {"owner": user})
        sales_count = frappe.db.count("Sale Invoice", {"owner": user})
        
        return {
            "shops": {
                "used": shops_count,
                "limit": shop_limit,
                "exceeded": shops_count >= shop_limit
            },
            "products": {
                "used": products_count,
                "limit": products_limit,
                "exceeded": products_count >= products_limit
            },
            "sales_invoices": {
                "used": sales_count,
                "limit": sales_invoice_limit if sales_invoice_limit else None,
                "exceeded": sales_count >= sales_invoice_limit if sales_invoice_limit else False
            }
        }
    
    except Exception as e:
        frappe.logger().error(f"❌ Error in check_user_limits: {str(e)}")
        # Return safe defaults on error
        return {
            "shops": {"used": 0, "limit": 1, "exceeded": False},
            "products": {"used": 0, "limit": 50, "exceeded": False},
            "sales_invoices": {"used": 0, "limit": 200, "exceeded": False}
        }

@frappe.whitelist(allow_guest=False)
def switch_to_free_plan():
    """Switch user to free plan immediately (no payment required)"""
    user = frappe.session.user
    
    # Get the Free Plan
    free_plan = frappe.db.get_value("Tookio Subscription", {"subscription_name": "Free Plan"}, "name")
    if not free_plan:
        frappe.throw("Free Plan not found")
    
    # Check if user already has a subscription record
    user_sub_name = frappe.db.exists("Tookio User Subscription", {"user": user})
    
    if user_sub_name:
        # Update existing subscription
        doc = frappe.get_doc("Tookio User Subscription", user_sub_name)
        frappe.logger().info(f"📄 Updating existing subscription {user_sub_name} to Free Plan")
    else:
        # Create new subscription record
        doc = frappe.new_doc("Tookio User Subscription")
        doc.user = user
        frappe.logger().info(f"📄 Creating new subscription for {user} with Free Plan")
    
    # Update subscription details to Free Plan
    doc.current_subscription = free_plan
    doc.subscription_start_date = frappe.utils.getdate()
    doc.subscription_end_date = None  # Free plan never expires
    doc.status = "Active"
    
    # Set free plan limits
    doc.shop_limit = 1
    doc.products_limit = 50
    doc.sales_invoice_limit = 200
    
    frappe.logger().info(f"💪 Set free plan limits: shops=1, products=50, invoices=200")
    
    # Save to trigger the hooks that populate limits and history
    doc.save(ignore_permissions=True)
    
    frappe.logger().info(f"✅ Switched to Free Plan successfully for {user}")
    
    frappe.db.commit()
    
    frappe.logger().info(f"🎉 Database committed - free plan switch complete for {user}")
    
    return {
        "success": True,
        "message": "Successfully switched to Free Plan!",
        "subscription": doc.name
    }
