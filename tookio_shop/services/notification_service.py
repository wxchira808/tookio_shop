"""
Notification Service for Tookio Shop
Handles low stock alerts, payment notifications, and social media reminders.

Key features:
- Low stock alerts when items hit zero/low threshold
- Payment received notifications
- Reminder to update TikTok/IG stories
"""

import frappe
from frappe import _
from frappe.utils import now_datetime


def send_low_stock_alert(product_name, remaining_qty, shop):
    """
    Send notification when product stock is low.
    Reminds seller to update their social media stories.
    """
    try:
        shop_doc = frappe.get_doc("Shop", shop)
        product = frappe.get_doc("Product", product_name)
        
        # Determine alert type
        if remaining_qty <= 0:
            alert_type = "out_of_stock"
            subject = f"🚨 OUT OF STOCK: {product.item_name}"
            message = f"'{product.item_name}' is now OUT OF STOCK! Remove from your TikTok/IG stories to avoid disappointing customers."
        elif remaining_qty <= 3:
            alert_type = "critical_low"
            subject = f"⚠️ CRITICAL LOW STOCK: {product.item_name}"
            message = f"Only {int(remaining_qty)} of '{product.item_name}' left! Consider restocking soon."
        else:
            alert_type = "low_stock"
            subject = f"📦 Low Stock: {product.item_name}"
            message = f"'{product.item_name}' is running low ({int(remaining_qty)} left)."

        # Create in-app notification
        create_tookio_notification(
            user=shop_doc.owner,
            notification_type="Low Stock",
            subject=subject,
            message=message,
            reference_doctype="Product",
            reference_name=product_name
        )

        # Real-time push
        frappe.publish_realtime(
            event="low_stock_alert",
            message={
                "type": alert_type,
                "product": product.item_name,
                "product_id": product_name,
                "remaining": remaining_qty,
                "shop": shop,
                "message": message
            },
            user=shop_doc.owner
        )

        frappe.logger().info(f"Low stock alert sent for {product.item_name} to {shop_doc.owner}")

    except Exception as e:
        frappe.log_error(f"Low stock alert error: {str(e)}", "Notification Service")


def send_payment_received_notification(order_name, mpesa_receipt, amount, shop):
    """
    Notify seller when payment is received via M-Pesa.
    """
    try:
        shop_doc = frappe.get_doc("Shop", shop)
        order = frappe.get_doc("Sales Order", order_name)

        subject = f"💰 Payment Received: KES {amount:,.0f}"
        message = f"Payment of KES {amount:,.0f} received for order {order_name}.\n"
        message += f"M-Pesa Receipt: {mpesa_receipt}\n"
        message += f"Customer: {order.customer_name}"

        # Create notification
        create_tookio_notification(
            user=shop_doc.owner,
            notification_type="Payment",
            subject=subject,
            message=message,
            reference_doctype="Sales Order",
            reference_name=order_name
        )

        # Real-time push
        frappe.publish_realtime(
            event="payment_received",
            message={
                "order": order_name,
                "amount": amount,
                "receipt": mpesa_receipt,
                "customer": order.customer_name,
                "shop": shop
            },
            user=shop_doc.owner
        )

        frappe.logger().info(f"Payment notification sent for {order_name} to {shop_doc.owner}")

    except Exception as e:
        frappe.log_error(f"Payment notification error: {str(e)}", "Notification Service")


def send_new_order_notification(order_name, shop, source):
    """
    Notify seller of new order from storefront or AI parser.
    """
    try:
        shop_doc = frappe.get_doc("Shop", shop)
        order = frappe.get_doc("Sales Order", order_name)

        subject = f"🛍️ New Order: {order.customer_name}"
        message = f"New order {order_name} from {source}.\n"
        message += f"Total: KES {order.total:,.0f}\n"
        message += f"Customer: {order.customer_name} ({order.customer_phone or 'No phone'})"

        # Create notification
        create_tookio_notification(
            user=shop_doc.owner,
            notification_type="New Order",
            subject=subject,
            message=message,
            reference_doctype="Sales Order",
            reference_name=order_name
        )

        # Real-time push
        frappe.publish_realtime(
            event="new_order",
            message={
                "order": order_name,
                "customer": order.customer_name,
                "total": order.total,
                "source": source,
                "shop": shop
            },
            user=shop_doc.owner
        )

    except Exception as e:
        frappe.log_error(f"New order notification error: {str(e)}", "Notification Service")


def create_tookio_notification(user, notification_type, subject, message, reference_doctype=None, reference_name=None):
    """
    Create a Tookio Notification record.
    """
    try:
        # Check if Tookio Notification DocType exists
        if not frappe.db.exists("DocType", "Notification"):
            # Fall back to system notification
            frappe.get_doc({
                "doctype": "Notification Log",
                "for_user": user,
                "subject": subject,
                "document_type": reference_doctype,
                "document_name": reference_name,
                "email_content": message
            }).insert(ignore_permissions=True)
            return

        doc = frappe.get_doc({
            "doctype": "Notification",
            "user": user,
            "notification_type": notification_type,
            "subject": subject,
            "message": message,
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "is_read": 0,
            "created_at": now_datetime()
        })
        doc.flags.ignore_permissions = True
        doc.insert()
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Create notification error: {str(e)}", "Notification Service")


# ==================== SCHEDULED TASKS ====================

def check_all_low_stock():
    """
    Scheduled task to check all products for low stock.
    Run daily to catch any missed alerts.
    """
    low_stock_products = frappe.get_all(
        "Product",
        filters={"enabled": 1, "stock_quantity": ["<=", 5]},
        fields=["name", "item_name", "stock_quantity", "shop", "owner"]
    )

    for product in low_stock_products:
        # Only alert if not already alerted recently
        recent_alert = frappe.db.exists(
            "Notification",
            {
                "reference_name": product.name,
                "notification_type": "Low Stock",
                "creation": [">", frappe.utils.add_days(frappe.utils.today(), -1)]
            }
        )

        if not recent_alert:
            send_low_stock_alert(product.name, product.stock_quantity, product.shop)


def send_daily_summary():
    """
    Send daily sales summary to sellers.
    Run at end of day.
    """
    from frappe.utils import today, add_days
    
    # Get all active shops
    shops = frappe.get_all(
        "Shop",
        filters={"enabled": 1},
        fields=["name", "shop_name", "owner"]
    )

    for shop in shops:
        try:
            # Get today's stats
            orders_today = frappe.db.count(
                "Sales Order",
                {"shop": shop.name, "order_date": today()}
            )

            revenue_today = frappe.db.sql("""
                SELECT COALESCE(SUM(total), 0) as total
                FROM `tabSales Order`
                WHERE shop = %s AND order_date = %s AND payment_status = 'Paid'
            """, (shop.name, today()), as_dict=True)[0].total or 0

            unpaid_orders = frappe.db.count(
                "Sales Order",
                {"shop": shop.name, "payment_status": "Unpaid", "order_status": ["!=", "Cancelled"]}
            )

            low_stock_count = frappe.db.count(
                "Product",
                {"shop": shop.name, "enabled": 1, "stock_quantity": ["<=", 5]}
            )

            if orders_today > 0 or unpaid_orders > 0:
                subject = f"📊 Daily Summary: {shop.shop_name}"
                message = f"""
Today's Summary for {shop.shop_name}:

📦 Orders Today: {orders_today}
💰 Revenue: KES {revenue_today:,.0f}
⏳ Unpaid Orders: {unpaid_orders}
📦 Low Stock Items: {low_stock_count}

Keep up the great work! 🚀
"""
                create_tookio_notification(
                    user=shop.owner,
                    notification_type="Daily Summary",
                    subject=subject,
                    message=message
                )

        except Exception as e:
            frappe.log_error(f"Daily summary error for {shop.name}: {str(e)}", "Daily Summary")
