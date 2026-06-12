import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop Pricing - Starter $3.50 and Pro $9"
    context.meta_description = "Compare Tookio Shop plans: Starter at $3.50 per month and Pro at $9 per month for growing online sellers."
    context.meta_keywords = "Tookio Shop pricing, Starter plan, Pro plan, inventory app pricing"
    return context
