import frappe
from frappe import _

def get_context(context):
    """
    Home page for Tookio Shop
    """
    context.no_cache = 1
    context.title = "Tookio Shop - Free Inventory Tracker & Online Seller Manager Kenya"
    
    # Set page metadata
    context.meta_description = "Tookio Shop helps Kenya's Online sellers and Online businesses track inventory, manage sales, and analyze performance. Free, mobile-friendly, and easy to use."
    context.meta_keywords = "free inventory tracker, kenya online seller manager, instagram sellers, whatsapp shop, small business, invoice, stock management, business analytics, tookio shop"
    
    return context
