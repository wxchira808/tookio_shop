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
def trigger_mpesa_payment(plan_name, phone_number):
    if not plan_name or not phone_number:
        frappe.throw(_("Plan and phone number are required."))

    try:
        plan = frappe.get_doc("Subscription Plan", plan_name)
        
        # Call the STK push function from tookio_mpesa app
        response = frappe.call(
            "tookio_mpesa.utils.initiate_stk_push_for_till",
            phone_number=phone_number,
            amount=plan.cost,
            account_reference=plan.name,
            transaction_desc=f"Payment for {plan.name}"
        )
        
        return response

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "M-Pesa Payment Error")
        frappe.throw(str(e))
