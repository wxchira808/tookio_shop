import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Tookio Shop - Inventory and Sales Control for Online Sellers"
    context.meta_description = "Tookio Shop helps online sellers manage inventory, sales invoices, purchases, shops and reporting. Starter is $3.50/month and Pro is $9/month."
    context.meta_keywords = "Tookio Shop, inventory management, online sellers, sales invoices, stock management, Kenya, Starter plan, Pro plan"
    return context
