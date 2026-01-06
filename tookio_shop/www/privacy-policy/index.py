import frappe
from frappe import _

def get_context(context):
    """
    Privacy Policy page for Tookio Shop
    """
    context.no_cache = 1
    context.title = "Privacy Policy - Tookio Shop"
    
    # Set page metadata
    context.meta_description = "Privacy Policy for Tookio Shop - Learn how we collect, use, and protect your personal information."
    context.meta_keywords = "privacy policy, data protection, tookio shop"
    
    return context