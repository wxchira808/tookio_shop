import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop Pricing - Free, Starter at $3.5 and Pro at $9"
    context.meta_description = "See Tookio Shop pricing. Start free, move to Starter at $3.5 per month, or Pro at $9 per month when your shop needs more room."
    context.meta_keywords = "Tookio Shop pricing, free plan, Starter plan, Pro plan, thrift seller app"
    return context
