import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop Subscription"
    context.meta_description = "Manage your Tookio Shop subscription. Starter is $3.50/month and Pro is $9/month."

    if frappe.session.user == "Guest":
        frappe.local.response["location"] = "/login"
        return

    context.current_plan_name = None
    context.current_status = None

    try:
        subscription_name = frappe.db.get_value("Tookio User Subscription", {"user": frappe.session.user}, "name")
        if subscription_name:
            subscription = frappe.get_doc("Tookio User Subscription", subscription_name)
            context.current_status = subscription.status
            if subscription.current_subscription:
                context.current_plan_name = frappe.db.get_value("Tookio Subscription", subscription.current_subscription, "subscription_name") or subscription.current_subscription
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Tookio Shop Subscription Page")

    context.plans = [
        {"name": "Starter", "price": "$3.50", "description": "For solo sellers and new shops that need reliable stock, sales and invoice records.", "features": ["Inventory and product tracking", "Sales invoices", "Purchase records", "Core reports", "Mobile app access"], "featured": False},
        {"name": "Pro", "price": "$9", "description": "For growing sellers who need more room, stronger reporting and priority support.", "features": ["Everything in Starter", "More room for products and sales", "Multi-shop structure", "Advanced sales and profit views", "Priority operational support"], "featured": True},
    ]
    return context
