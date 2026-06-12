import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop - Simple stock and sales tracking for everyday sellers"
    context.meta_description = "Tookio Shop helps everyday sellers track stock, sales and spending in one place. Start free, then move to Starter or Pro if you need more."
    context.meta_keywords = "Tookio Shop, thrift sellers, stock tracker, online sellers, free plan, Starter plan, Pro plan"
    return context
