import frappe
from frappe import _

def get_context(context):
    """
    Checkout page for subscription plans
    """
    context.no_cache = 1
    
    # Redirect guests to login page
    if frappe.session.user == "Guest":
        frappe.local.response["location"] = "/login"
        return

    # Get the selected plan from URL parameter
    plan_name = frappe.form_dict.get("plan")
    if not plan_name:
        frappe.local.response["location"] = "/subscriptions"
        return

    try:
        # Get the subscription plan details
        plan = frappe.get_doc("Subscription Plan", plan_name)
        context.plan = plan
        
        # Get current user details
        customer_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")
        if customer_name:
            customer = frappe.get_doc("Customer", customer_name)
            context.customer = customer
        else:
            context.customer = None
        
    except Exception as e:
        frappe.log_error(f"Error in checkout for plan {plan_name}: {e}", "Checkout Error")
        context.error = _("Could not load checkout details. Please try again.")

@frappe.whitelist(allow_guest=False)
def confirm_payment(plan_name, phone_number, transaction_code):
    """Confirm payment and create subscription"""
    if not plan_name or not phone_number:
        frappe.throw(_("Plan and phone number are required."))

    try:
        # Get the plan details
        plan = frappe.get_doc("Subscription Plan", plan_name)
        
        # Get current user's customer record
        customer_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")
        if not customer_name:
            frappe.throw(_("No customer record found for your account."))
        
        customer = frappe.get_doc("Customer", customer_name)
        
        # Create a draft Sales Invoice for tracking
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = customer_name
        sales_invoice.posting_date = frappe.utils.today()
        sales_invoice.due_date = frappe.utils.add_days(frappe.utils.today(), 30)
        sales_invoice.company = frappe.defaults.get_user_default("Company")
        sales_invoice.currency = "KES"
        
        # Add custom fields for tracking
        sales_invoice.custom_phone_number = phone_number
        sales_invoice.custom_transaction_id = transaction_code
        
        # Add the subscription plan as an invoice item
        sales_invoice.append("items", {
            "item_code": plan.item,
            "item_name": plan.name,
            "description": f"Subscription to {plan.name} - Till Payment Confirmation Code: {transaction_code}",
            "qty": 1,
            "rate": plan.cost,
            "amount": plan.cost
        })
        
        # Add payment details in remarks
        sales_invoice.remarks = f"M-Pesa Till Payment - Till No: 6547212, Phone: {phone_number}, Confirmation Code: {transaction_code}, Date: {frappe.utils.now()}"
        
        # Save as draft (will be manually verified and submitted later)
        sales_invoice.insert(ignore_permissions=True)
        
        # Update customer's subscription plan
        customer.custom_tookio_subscription_plan = plan.name
        customer.save(ignore_permissions=True)
        
        # Create or update subscription record
        existing_subscription = frappe.db.get_value(
            "Subscription", 
            {"party": customer_name}, 
            "name"
        )
        
        if existing_subscription:
            # Update existing subscription
            subscription = frappe.get_doc("Subscription", existing_subscription)
            subscription.plans = []  # Clear existing plans
            subscription.append("plans", {
                "plan": plan.name,
                "qty": 1
            })
            subscription.status = "Active"
            subscription.current_invoice_start = frappe.utils.today()
            subscription.current_invoice_end = frappe.utils.add_months(frappe.utils.today(), 1)
            subscription.save(ignore_permissions=True)
        else:
            # Create new subscription
            subscription = frappe.new_doc("Subscription")
            subscription.party_type = "Customer"
            subscription.party = customer_name
            subscription.status = "Active"
            subscription.current_invoice_start = frappe.utils.today()
            subscription.current_invoice_end = frappe.utils.add_months(frappe.utils.today(), 1)
            subscription.append("plans", {
                "plan": plan.name,
                "qty": 1
            })
            subscription.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "message": _("Payment confirmed! Your subscription has been activated."),
            "sales_invoice": sales_invoice.name,
            "subscription": subscription.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payment Confirmation Error")
        frappe.throw(str(e))
