import frappe
from frappe import _

def get_context(context):
    """
    Home page for Tookio Shop
    """
    context.no_cache = 1
    context.title = "Tookio - Empower Your Online Shop for FREE"
    
    # Set page metadata
    context.meta_description = "Professional Shop Assistant & Inventory Manager for Instagram, WhatsApp & Online Sellers. Start selling now - FREE!"
    context.meta_keywords = "online shop, inventory management, instagram seller, whatsapp business, e-commerce, free"
    
    return context
