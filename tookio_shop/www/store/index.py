"""
Link-in-Bio Storefront for Tookio Shop
Public page that sellers can share on TikTok, Instagram, WhatsApp.

URL: /store?shop=SHOP-XX-XX-XX-XXX
"""

import frappe
from frappe import _


def get_context(context):
    """
    Build context for the storefront page.
    Shows shop products with stock levels and M-Pesa payment option.
    """
    context.no_cache = 1
    
    # Get shop from query params
    shop_id = frappe.form_dict.get("shop")
    
    if not shop_id:
        context.title = "Store Not Found"
        context.error = "No shop specified. Please use a valid store link."
        context.shop = None
        context.products = []
        return context

    # Get shop details
    try:
        shop = frappe.get_doc("Shop", shop_id)
        
        if not shop.enabled:
            context.title = "Store Unavailable"
            context.error = "This store is currently unavailable."
            context.shop = None
            context.products = []
            return context

        context.shop = shop
        context.title = f"{shop.shop_name} | Tookio Store"
        
    except frappe.DoesNotExistError:
        context.title = "Store Not Found"
        context.error = "This store doesn't exist. Please check the link."
        context.shop = None
        context.products = []
        return context

    # Get products with stock
    products = frappe.get_all(
        "Product",
        filters={"shop": shop_id, "enabled": 1},
        fields=["name", "item_name", "selling_price", "stock_quantity", "photo", "uom"],
        order_by="item_name"
    )

    # Enhance product data
    for product in products:
        product["in_stock"] = product.stock_quantity > 0
        product["formatted_price"] = f"KES {product.selling_price:,.2f}" if product.selling_price else "Price on request"
        product["stock_status"] = get_stock_status(product.stock_quantity)

    context.products = products
    context.product_count = len(products)
    context.in_stock_count = len([p for p in products if p["in_stock"]])

    # Check if M-Pesa is configured
    mpesa_settings = frappe.db.get_value(
        "M-Pesa Settings",
        {"shop": shop_id, "enabled": 1},
        ["shortcode", "business_type"],
        as_dict=True
    )
    context.mpesa_enabled = bool(mpesa_settings)
    context.mpesa_shortcode = mpesa_settings.shortcode if mpesa_settings else None
    context.mpesa_type = mpesa_settings.business_type if mpesa_settings else None

    # Meta tags for social sharing
    context.meta_description = f"Shop at {shop.shop_name} - {context.in_stock_count} items in stock. Pay with M-Pesa!"
    context.meta_image = shop.shop_logo if shop.shop_logo else "/assets/tookio_shop/images/default-store.png"

    return context


def get_stock_status(qty):
    """Get human-readable stock status"""
    if qty <= 0:
        return {"text": "Out of Stock", "color": "red", "badge": "danger"}
    elif qty <= 3:
        return {"text": "Low Stock", "color": "orange", "badge": "warning"}
    elif qty <= 10:
        return {"text": "Limited", "color": "yellow", "badge": "info"}
    else:
        return {"text": "In Stock", "color": "green", "badge": "success"}
