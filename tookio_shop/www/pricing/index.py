import frappe
from frappe import _

def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop - FREE Forever! | Free Inventory Management Kenya"
    context.meta_description = "Tookio Shop is now completely FREE! Unlimited inventory management for Kenyan online sellers. No subscriptions, no payments - just free forever."
    context.meta_keywords = "tookio shop free, free inventory tracker kenya, free online seller app, free whatsapp shop, free business management"
    return context
