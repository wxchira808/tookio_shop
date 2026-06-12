import frappe


PLANS = {
    "starter": {"name": "Starter", "price": "$3.50", "description": "For solo sellers and small shops moving away from manual records."},
    "pro": {"name": "Pro", "price": "$9", "description": "For growing sellers with more products, more sales activity and sharper reporting needs."},
}


def get_context(context):
    context.no_cache = 1
    context.title = "Activate Tookio Shop"
    plan_key = (frappe.form_dict.get("plan") or "starter").lower().strip()
    context.plan = PLANS.get(plan_key, PLANS["starter"])
    return context
