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


def normalize_user_identifier(user_identifier):
    if not user_identifier:
        return user_identifier

    if frappe.db.exists("User", user_identifier):
        return user_identifier

    resolved_user = frappe.db.get_value("User", {"email": user_identifier}, "name")
    return resolved_user or user_identifier


def ensure_user_subscription_record(user_identifier):
    normalized_user = normalize_user_identifier(user_identifier)
    if not normalized_user or normalized_user == "Guest":
        return None

    existing = frappe.db.exists("Tookio User Subscription", {"user": normalized_user})
    if existing:
        return existing

    free_plan = frappe.db.get_value("Tookio Subscription", {"subscription_name": "Free Plan"}, "name")
    if not free_plan:
        frappe.log_error("Free Plan not found", "Auto Subscription Creation")
        return None

    user_sub = frappe.new_doc("Tookio User Subscription")
    user_sub.user = normalized_user
    user_sub.current_subscription = free_plan
    user_sub.subscription_start_date = frappe.utils.getdate()
    user_sub.subscription_end_date = None
    user_sub.status = "Active"
    user_sub.insert(ignore_permissions=True)

    frappe.db.commit()
    return user_sub.name


@frappe.whitelist(allow_guest=False)
def get_user_subscription():
    """Get current user's subscription details"""
    from frappe.utils import today, getdate
    
    try:
        session_user = frappe.session.user

        # Resolve the actual User DocType name as defensively as possible.
        # Some logins come through as email while the linked User name can differ.
        resolved_user = session_user
        if session_user and session_user != "Guest":
            try:
                user_doc = frappe.get_doc("User", session_user)
                resolved_user = user_doc.name or session_user
            except Exception:
                user_name = frappe.db.get_value("User", {"email": session_user}, "name")
                if user_name:
                    resolved_user = user_name
                else:
                    user_email = frappe.db.get_value("User", {"name": session_user}, "email")
                    if user_email:
                        resolved_user = user_email
        
        # Get user subscription
        user_sub = frappe.db.exists("Tookio User Subscription", {"user": resolved_user})
        if not user_sub and resolved_user != session_user:
            user_sub = frappe.db.exists("Tookio User Subscription", {"user": session_user})

        if not user_sub:
            user_sub = ensure_user_subscription_record(resolved_user)

        if user_sub:
            doc = frappe.get_doc("Tookio User Subscription", user_sub)
            
            # Check if subscription has expired and auto-downgrade
            try:
                if doc.subscription_end_date:
                    end_date = getdate(doc.subscription_end_date)
                    current_date = getdate(today())
                    
                    if current_date > end_date and doc.status != "Expired":
                        frappe.logger().info(f"🔄 Auto-downgrading expired subscription for {resolved_user} to Free Plan")
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
            current_shops = frappe.db.count("Shop", {"owner": resolved_user})
            current_products = frappe.db.count("Product", {"owner": resolved_user})
            current_sales_invoices = frappe.db.count("Sale Invoice", {"owner": resolved_user})
            
            # Get subscription plan name
            plan_name = "Free Plan"
            if doc.current_subscription and doc.current_subscription != "Free Plan":
                try:
                    plan_doc = frappe.get_doc("Tookio Subscription", doc.current_subscription)
                    plan_name = plan_doc.subscription_name
                except:
                    plan_name = doc.current_subscription
            
            return {
                "name": doc.name,
                "subscription_record_name": doc.name,
                "user": doc.user,
                "resolved_user": resolved_user,
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
            current_shops = frappe.db.count("Shop", {"owner": resolved_user})
            current_products = frappe.db.count("Product", {"owner": resolved_user})
            current_sales_invoices = frappe.db.count("Sale Invoice", {"owner": resolved_user})
            
            return {
                "name": None,
                "subscription_record_name": None,
                "user": resolved_user,
                "resolved_user": resolved_user,
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
            "name": None,
            "subscription_record_name": None,
            "user": None,
            "resolved_user": None,
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

@frappe.whitelist(allow_guest=True)
def user_signup(email, full_name, password):
    """
    Standard signup for mobile app that allows setting password immediately.
    """
    if not email or not full_name or not password:
        frappe.throw(frappe._("All fields (email, full_name, password) are required"))

    if frappe.db.exists("User", email):
        frappe.throw(frappe._("User with email {0} already exists").format(email))

    try:
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "enabled": 1,
            "new_password": password,
            "user_type": "Website User"
        })
        user.flags.ignore_permissions = True
        user.insert()

        # Generate API Keys for the user
        from frappe.core.doctype.user.user import generate_keys
        api_keys = generate_keys(user.name)

        # Commit so the user is in the DB
        frappe.db.commit()

        return {
            "success": True,
            "message": frappe._("User created successfully"),
            "api_key": api_keys.get("api_key"),
            "api_secret": api_keys.get("api_secret")
        }
    except Exception as e:
        frappe.log_error(f"Signup error for {email}: {str(e)}", "User Signup Error")
        frappe.throw(str(e))


# ==================== SUBSCRIPTION RENEWAL WITH M-PESA ====================

@frappe.whitelist()
def get_available_subscriptions():
	"""Get all enabled subscription plans for renewal"""
	plans = frappe.get_all(
		"Tookio Subscription",
		filters={"enabled": 1},
		fields=["name", "subscription_name", "description", "price", "currency", 
		        "shop_limit", "products_limit", "sales_invoice_limit"],
		order_by="price asc"
	)
	return plans


def resolve_current_user_subscription(subscription_name=None):
    """Resolve a Tookio User Subscription document safely.
    If a specific subscription name is provided, use it when valid.
    Otherwise, fall back to the current session user's subscription row.
    """
    def is_missing(value):
        if value is None:
            return True
        if isinstance(value, (dict, list, tuple)):
            return True
        return str(value).strip().lower() in {"", "none", "null", "undefined"}

    if not is_missing(subscription_name):
        try:
            return frappe.get_doc("Tookio User Subscription", subscription_name)
        except Exception:
            pass

    subscription_data = get_user_subscription()
    record_name = subscription_data.get("name") or subscription_data.get("subscription_record_name")
    if not is_missing(record_name):
        return frappe.get_doc("Tookio User Subscription", record_name)

    resolved_user = subscription_data.get("resolved_user") or subscription_data.get("user") or frappe.session.user
    created_record = ensure_user_subscription_record(resolved_user)
    if created_record:
        return frappe.get_doc("Tookio User Subscription", created_record)

    frappe.throw("No subscription record found for the current user")


@frappe.whitelist()
def calculate_subscription_upgrade_cost(user_subscription=None, new_subscription=None):
	"""
	Calculate the cost of upgrading to a new subscription plan
	Takes into account prorated credit from remaining days on current plan
	"""
	from frappe.utils import getdate, date_diff, today
	
	# Get user subscription document
	user_sub = resolve_current_user_subscription(user_subscription)
	
	# Get new subscription plan
	new_plan = frappe.get_doc("Tookio Subscription", new_subscription)
	
	# Calculate credit from current plan
	credit_from_old_plan = 0
	days_remaining = 0
	
	if user_sub.current_subscription and user_sub.subscription_end_date:
		# Get current plan
		current_plan = frappe.get_doc("Tookio Subscription", user_sub.current_subscription)
		
		# Calculate days remaining
		end_date = getdate(user_sub.subscription_end_date)
		current_date = getdate(today())
		days_remaining = date_diff(end_date, current_date)
		
		if days_remaining > 0:
			# Calculate prorated credit (assuming 30 days per month)
			daily_rate = current_plan.price / 30
			credit_from_old_plan = daily_rate * days_remaining
	
	# Calculate amount to pay
	amount_to_pay = new_plan.price - credit_from_old_plan
	
	# Ensure amount is not negative
	if amount_to_pay < 0:
		amount_to_pay = 0
	
	# Determine if it's an upgrade or downgrade
	is_upgrade = False
	if user_sub.current_subscription:
		current_plan = frappe.get_doc("Tookio Subscription", user_sub.current_subscription)
		is_upgrade = new_plan.price > current_plan.price
	
	return {
		"new_plan_price": new_plan.price,
		"credit_from_old_plan": credit_from_old_plan,
		"days_remaining": days_remaining,
		"amount_to_pay": round(amount_to_pay, 2),
		"is_upgrade": is_upgrade,
		"currency": new_plan.currency
	}


@frappe.whitelist()
def initiate_subscription_payment(user_subscription=None, new_subscription=None, phone_number=None, amount=None):
	"""
	Initiate M-Pesa STK Push payment for subscription upgrade/renewal
	"""
	import sys
	sys.path.append('/home/brian/frappe-bench/apps/tookio_mpesa')
	
	from tookio_mpesa.utils import initiate_stk_push_for_till
	
	try:
		# Get user subscription document
		user_sub = resolve_current_user_subscription(user_subscription)
		
		# Get new subscription plan
		new_plan = frappe.get_doc("Tookio Subscription", new_subscription)
		
		# Prepare transaction description
		account_reference = f"SUB-{user_sub.name}"
		transaction_desc = f"Subscription to {new_plan.subscription_name}"
		
		# Initiate STK Push
		response = initiate_stk_push_for_till(
			phone_number=phone_number,
			amount=amount,
			account_reference=account_reference,
			transaction_desc=transaction_desc
		)
		
		# Get the created transaction
		checkout_request_id = response.get("CheckoutRequestID")
		
		if checkout_request_id:
			# Find the transaction that was just created
			transaction = frappe.get_last_doc("Mpesa Transaction", 
				filters={"checkout_request_id": checkout_request_id})
			
			# Link the subscription upgrade details to the transaction
			# We'll store this in a custom field or use account_reference to track
			transaction.db_set("account_reference", f"{user_sub.name}|{new_subscription}", update_modified=False)
			frappe.db.commit()
			
			return {
				"success": True,
				"transaction_id": transaction.name,
				"checkout_request_id": checkout_request_id,
				"message": response.get("CustomerMessage", "STK Push sent to your phone")
			}
		else:
			return {
				"success": False,
				"message": "Failed to initiate payment"
			}
	
	except Exception as e:
		frappe.log_error(f"Subscription payment initiation failed: {str(e)}", "Subscription Payment")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def check_subscription_payment_status(transaction_id):
	"""Check the status of a subscription payment transaction"""
	try:
		transaction = frappe.get_doc("Mpesa Transaction", transaction_id)
		
		# If payment is successful and not yet processed
		if transaction.status == "Success" and transaction.account_reference:
			# Check if we haven't already processed this payment
			if "|" in transaction.account_reference:
				parts = transaction.account_reference.split("|")
				if len(parts) == 2:
					user_subscription = parts[0]
					new_subscription = parts[1]
					
					# Check if this payment has already been processed
					# by verifying if the subscription was already updated
					user_sub = resolve_current_user_subscription(user_subscription)
					
					# Only process if current subscription doesn't match the paid one
					if user_sub.current_subscription != new_subscription:
						# Process the subscription upgrade
						process_subscription_upgrade(user_subscription, new_subscription, transaction.name)
		
		return {
			"status": transaction.status,
			"result_desc": transaction.result_desc,
			"mpesa_receipt_number": transaction.mpesa_receipt_number
		}
	
	except Exception as e:
		frappe.log_error(f"Error checking payment status: {str(e)}", "Subscription Payment Status")
		return {
			"status": "Error",
			"result_desc": str(e)
		}


def process_subscription_upgrade(user_subscription, new_subscription, transaction_id):
	"""
	Process subscription upgrade after successful payment
	Updates user subscription and creates history record
	"""
	from frappe.utils import getdate, add_months, today
	
	try:
		# Get documents
        user_sub = resolve_current_user_subscription(user_subscription)
		new_plan = frappe.get_doc("Tookio Subscription", new_subscription)
		
		# Store old subscription details for history
		old_subscription = user_sub.current_subscription
		old_start_date = user_sub.subscription_start_date
		old_end_date = user_sub.subscription_end_date
		old_status = user_sub.status
		
		# Update subscription
		user_sub.current_subscription = new_subscription
		user_sub.subscription_start_date = getdate(today())
		user_sub.subscription_end_date = add_months(getdate(today()), 1)  # 1 month subscription
		user_sub.status = "Active"
		
		# Update limits from new plan
		user_sub.shop_limit = new_plan.shop_limit
		user_sub.products_limit = new_plan.products_limit
		user_sub.sales_invoice_limit = new_plan.sales_invoice_limit
		
		# Add old subscription to history (manually, before save triggers automatic history)
		if old_subscription:
			user_sub.append("subscription_history", {
				"tookio_subscription": old_subscription,
				"subscription_start_date": old_start_date,
				"subscription_end_date": old_end_date,
				"status": "Replaced"
			})
		
		# Save the subscription (this will also add the new one to history via on_update hook)
		user_sub.save(ignore_permissions=True)
		frappe.db.commit()
		
		# Log the upgrade
		frappe.logger().info(f"✅ Subscription upgraded for {user_sub.user} from {old_subscription} to {new_subscription} (Transaction: {transaction_id})")
		
		# Send notification email
		try:
			frappe.sendmail(
				recipients=[user_sub.user_email],
				subject="Subscription Upgraded Successfully",
				message=f"""
					<h3>Your subscription has been upgraded!</h3>
					<p>Your Tookio Shop subscription has been successfully upgraded to <strong>{new_plan.subscription_name}</strong>.</p>
					<p><strong>New Limits:</strong></p>
					<ul>
						<li>Shops: {new_plan.shop_limit}</li>
						<li>Products: {new_plan.products_limit}</li>
						<li>Sales Invoices: {new_plan.sales_invoice_limit}</li>
					</ul>
					<p>Valid until: {user_sub.subscription_end_date}</p>
					<p>M-Pesa Receipt: {transaction_id}</p>
				"""
			)
		except Exception as email_error:
			frappe.log_error(f"Failed to send upgrade email: {str(email_error)}", "Subscription Email")
		
		return True
	
	except Exception as e:
		frappe.log_error(f"Failed to process subscription upgrade: {str(e)}", "Subscription Upgrade")
		frappe.throw(f"Failed to upgrade subscription: {str(e)}")


@frappe.whitelist(allow_guest=True)
def subscription_payment_webhook():
	"""
	Webhook endpoint to handle M-Pesa payment callbacks for subscriptions
	This is called by M-Pesa after payment is processed
	"""
	try:
		# Get the callback data from M-Pesa
		# The tookio_mpesa.utils.stk_callback already handles updating the transaction
		# We just need to check for completed payments and process subscription upgrades
		
		callback_data = json.loads(frappe.request.data)
		stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
		checkout_request_id = stk_callback.get("CheckoutRequestID")
		result_code = stk_callback.get("ResultCode")
		
		if result_code == 0:  # Success
			# Find the transaction
			transaction = frappe.get_doc("Mpesa Transaction", 
				{"checkout_request_id": checkout_request_id})
			
			if transaction and transaction.account_reference:
				# Check if this is a subscription payment
				if "|" in transaction.account_reference:
					parts = transaction.account_reference.split("|")
					if len(parts) == 2:
						user_subscription = parts[0]
						new_subscription = parts[1]
						
						# Process the subscription upgrade
						process_subscription_upgrade(user_subscription, new_subscription, transaction.name)
		
		return {"ResultCode": 0, "ResultDesc": "Success"}
	
	except Exception as e:
		frappe.log_error(f"Subscription webhook error: {str(e)}", "Subscription Webhook")
		return {"ResultCode": 1, "ResultDesc": "Error processing webhook"}

