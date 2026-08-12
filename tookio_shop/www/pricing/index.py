import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop Pricing - Free, Starter, Pro and Premium"
    context.meta_description = "Compare Tookio Shop plans for stock, sales, multi-shop management, and online websites."
    context.meta_keywords = "Tookio Shop pricing, free plan, Starter plan, Pro plan, Premium plan"
    return context
