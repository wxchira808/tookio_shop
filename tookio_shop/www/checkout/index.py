import frappe


PLANS = {
    "starter": {"name": "Starter", "price": "KES 450", "description": "For one growing shop with stock, sales, and expense records."},
    "pro": {"name": "Pro", "price": "KES 1,000", "description": "For unlimited shops and one public Tookio Website."},
    "premium": {"name": "Premium", "price": "KES 2,500", "description": "For unlimited shops and up to five separate Tookio Websites."},
}


def get_context(context):
    context.no_cache = 1
    context.title = "Activate Tookio Shop"
    plan_key = (frappe.form_dict.get("plan") or "starter").lower().strip()
    context.plan = PLANS.get(plan_key, PLANS["starter"])
    return context
