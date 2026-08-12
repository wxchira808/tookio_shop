import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop Subscription"
    context.meta_description = "Manage your Tookio Shop subscription and online website access."

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

    context.plans = frappe.get_all(
        "Tookio Subscription",
        filters={"enabled": 1},
        fields=["subscription_name as name", "price", "currency", "description", "shop_limit", "products_limit", "sales_invoice_limit", "website_enabled", "website_limit"],
        order_by="price asc",
    )
    for plan in context.plans:
        plan.price = f"{plan.currency} {plan.price:,.0f}"
        plan.features = [
            _limit_label("Shop", plan.shop_limit),
            _limit_label("Product", plan.products_limit),
            _limit_label("Sales invoice", plan.sales_invoice_limit),
            _limit_label("Tookio Website", plan.website_limit) if plan.website_enabled else "No public Tookio Website",
        ]
        plan.featured = plan.name == "Pro Plan"
    return context


def _limit_label(label, limit):
    return f"Unlimited {label}s" if limit == 0 else f"Up to {limit} {label}{'' if limit == 1 else 's'}"
