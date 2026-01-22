"""
Storefront API for Tookio Shop
Public-facing APIs for the Link-in-Bio storefront.
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_store(shop_id):
    """
    Get public store information and products.
    Used by storefront page and mobile apps.
    
    Args:
        shop_id: Shop docname
    
    Returns:
        Store info with products
    """
    try:
        shop = frappe.get_doc("Shop", shop_id)
        
        if not shop.enabled:
            return {"error": "Store unavailable", "available": False}

        # Get products
        products = frappe.get_all(
            "Product",
            filters={"shop": shop_id, "enabled": 1},
            fields=["name", "item_name", "selling_price", "stock_quantity", "photo", "uom"],
            order_by="item_name"
        )

        # Check M-Pesa status
        mpesa = frappe.db.get_value(
            "M-Pesa Settings",
            {"shop": shop_id, "enabled": 1},
            ["shortcode", "business_type"],
            as_dict=True
        )

        return {
            "available": True,
            "shop": {
                "name": shop.name,
                "shop_name": shop.shop_name,
                "location": shop.location,
                "mobile_number": shop.mobile_number,
                "logo": shop.shop_logo
            },
            "products": products,
            "mpesa_enabled": bool(mpesa),
            "mpesa_shortcode": mpesa.shortcode if mpesa else None,
            "mpesa_type": mpesa.business_type if mpesa else None
        }

    except frappe.DoesNotExistError:
        return {"error": "Store not found", "available": False}


@frappe.whitelist(allow_guest=True)
def create_customer_order(shop_id, customer_phone, delivery_location, items, customer_name=None):
    """
    Create an order from the public storefront.
    This is a guest API - no authentication required.
    
    Args:
        shop_id: Shop docname
        customer_phone: Customer's phone number
        delivery_location: Delivery address
        items: List of {product_id, quantity}
        customer_name: Optional customer name
    
    Returns:
        Order details
    """
    import json
    
    if isinstance(items, str):
        items = json.loads(items)

    # Validate shop
    shop = frappe.get_doc("Shop", shop_id)
    if not shop.enabled:
        frappe.throw("This store is not accepting orders")

    # Create order
    order = frappe.new_doc("Sales Order")
    order.shop = shop_id
    order.order_source = "Storefront"
    order.order_status = "Draft"
    order.payment_status = "Unpaid"
    order.customer_name = customer_name or "Customer"
    order.customer_phone = customer_phone
    order.delivery_location = delivery_location

    # Add items
    total = 0
    for item in items:
        product = frappe.get_doc("Product", item.get("product_id"))
        
        qty = item.get("quantity", 1)
        rate = product.selling_price or 0
        amount = qty * rate
        total += amount

        order.append("items", {
            "product": product.name,
            "item_name": product.item_name,
            "qty": qty,
            "rate": rate,
            "amount": amount
        })

    order.subtotal = total
    order.total = total
    
    # Set owner to shop owner so they see it
    order.flags.ignore_permissions = True
    order.owner = shop.owner
    order.insert()

    # Notify shop owner
    frappe.publish_realtime(
        event="new_order",
        message={
            "order": order.name,
            "customer": order.customer_name,
            "total": order.total,
            "source": "Storefront"
        },
        user=shop.owner
    )

    return {
        "success": True,
        "order_id": order.name,
        "total": order.total,
        "message": f"Order {order.name} created. You'll be contacted soon."
    }


@frappe.whitelist(allow_guest=True)
def request_mpesa_stk(shop_id, order_id, phone_number):
    """
    Request M-Pesa STK Push for a storefront order.
    Customer can pay directly from the storefront.
    
    Args:
        shop_id: Shop docname
        order_id: Order to pay for
        phone_number: Customer's M-Pesa phone number
    
    Returns:
        STK Push status
    """
    from tookio_shop.tookio_shop.doctype.tookio_m_pesa_settings.tookio_m_pesa_settings import get_mpesa_settings_for_shop

    # Validate order belongs to shop
    order = frappe.get_doc("Sales Order", order_id)
    if order.shop != shop_id:
        frappe.throw("Invalid order")

    if order.payment_status == "Paid":
        return {"success": False, "error": "Order already paid"}

    # Get M-Pesa settings
    mpesa = get_mpesa_settings_for_shop(shop_id)
    if not mpesa:
        return {
            "success": False,
            "error": "M-Pesa not configured for this store. Please pay via WhatsApp."
        }

    # Initiate STK Push
    result = mpesa.initiate_stk_push(
        phone_number=phone_number,
        amount=order.total,
        account_reference=order_id,
        description=f"Order {order_id}"
    )

    return result


@frappe.whitelist(allow_guest=True)
def check_order_payment(order_id):
    """
    Check if an order has been paid.
    Used for polling after STK Push.
    
    Args:
        order_id: Order docname
    
    Returns:
        Payment status
    """
    payment_status = frappe.db.get_value(
        "Sales Order",
        order_id,
        ["payment_status", "mpesa_receipt"],
        as_dict=True
    )

    if not payment_status:
        return {"error": "Order not found"}

    return {
        "paid": payment_status.payment_status == "Paid",
        "status": payment_status.payment_status,
        "receipt": payment_status.mpesa_receipt
    }


@frappe.whitelist(allow_guest=True)
def get_store_url(shop_id):
    """
    Get the shareable store URL for a shop.
    """
    base_url = frappe.utils.get_url()
    return {
        "url": f"{base_url}/store?shop={shop_id}",
        "short_url": f"{base_url}/store?shop={shop_id}"  # Can integrate with URL shortener
    }
