# Copyright (c) 2026, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, flt


class SalesOrder(Document):
    """
    Sales Order with social commerce workflow:
    Draft → Confirmed → Processing → Ready → Completed
    
    Payment: Unpaid → Partial → Paid
    Fulfillment: Pending → Packing → Shipped → Delivered
    
    Integrates with M-Pesa for automatic payment reconciliation.
    """

    def validate(self):
        """Calculate totals and validate stock"""
        self.calculate_totals()
        self.validate_stock_availability()

    def before_save(self):
        """Update status based on payment and fulfillment"""
        self.update_order_status()

    def after_insert(self):
        """Notify seller of new order"""
        if self.order_source != "Manual":
            self.notify_new_order()

    def calculate_totals(self):
        """Calculate subtotal and total from items"""
        self.subtotal = 0
        for item in self.items:
            item_total = flt(item.qty) * flt(item.rate)
            item.amount = item_total
            self.subtotal += item_total

        self.total = flt(self.subtotal) + flt(self.delivery_fee) - flt(self.discount)

    def validate_stock_availability(self):
        """Check if items are in stock (warning only for draft)"""
        if self.order_status == "Draft":
            return  # Skip validation for drafts

        for item in self.items:
            if item.product:
                stock_qty = frappe.db.get_value("Product", item.product, "stock_quantity")
                if flt(stock_qty) < flt(item.qty):
                    frappe.msgprint(
                        f"Warning: {item.item_name} only has {stock_qty} in stock, but {item.qty} ordered.",
                        indicator="orange",
                        alert=True
                    )

    def update_order_status(self):
        """Auto-update order status based on payment and fulfillment"""
        # If paid and delivered, mark as completed
        if self.payment_status == "Paid" and self.fulfillment_status == "Delivered":
            self.order_status = "Completed"
        # If shipped, mark as processing
        elif self.fulfillment_status == "Shipped":
            self.order_status = "Processing"
        # If ready to ship, mark as ready
        elif self.fulfillment_status == "Packing":
            self.order_status = "Ready"

    def notify_new_order(self):
        """Send real-time notification to seller"""
        try:
            shop_owner = frappe.db.get_value("Shop", self.shop, "owner")
            
            frappe.publish_realtime(
                event="new_order",
                message={
                    "order": self.name,
                    "customer": self.customer_name,
                    "total": self.total,
                    "source": self.order_source
                },
                user=shop_owner
            )
        except Exception as e:
            frappe.log_error(f"Order notification error: {str(e)}", "Order Notification")

    def request_mpesa_payment(self):
        """
        Initiate STK Push for this order.
        Called from the order form button.
        """
        from tookio_shop.api.mpesa import initiate_stk_push

        if not self.customer_phone:
            frappe.throw("Customer phone number is required for M-Pesa payment")

        result = initiate_stk_push(
            shop=self.shop,
            phone_number=self.customer_phone,
            amount=self.total,
            order_reference=self.name,
            description=f"Order {self.name}"
        )

        return result

    def mark_as_paid(self, mpesa_receipt=None, amount=None):
        """Manually mark order as paid"""
        self.payment_status = "Paid"
        self.paid_amount = amount or self.total
        self.payment_date = now_datetime()
        if mpesa_receipt:
            self.mpesa_receipt = mpesa_receipt
        self.save()

    def deduct_stock(self):
        """
        Deduct stock when order is confirmed.
        Should be called when order_status changes to 'Confirmed'.
        """
        for item in self.items:
            if item.product:
                product = frappe.get_doc("Product", item.product)
                new_qty = flt(product.stock_quantity) - flt(item.qty)
                
                if new_qty < 0:
                    frappe.throw(f"Not enough stock for {item.item_name}")
                
                product.db_set("stock_quantity", new_qty)

                # Check for low stock alert
                if new_qty <= 5:
                    self.trigger_low_stock_alert(product.name, new_qty)

    def trigger_low_stock_alert(self, product_name, remaining_qty):
        """Send low stock notification to seller"""
        try:
            shop_owner = frappe.db.get_value("Shop", self.shop, "owner")
            product = frappe.get_doc("Product", product_name)

            frappe.publish_realtime(
                event="low_stock",
                message={
                    "product": product.item_name,
                    "remaining": remaining_qty,
                    "shop": self.shop
                },
                user=shop_owner
            )

            # Create system notification
            frappe.get_doc({
                "doctype": "Notification",
                "user": shop_owner,
                "notification_type": "Low Stock",
                "subject": f"Low Stock Alert: {product.item_name}",
                "message": f"Only {remaining_qty} left. Update your TikTok/IG stories!",
                "reference_doctype": "Product",
                "reference_name": product_name
            }).insert(ignore_permissions=True)

            frappe.logger().info(f"Low stock alert sent for {product.item_name}")

        except Exception as e:
            frappe.log_error(f"Low stock alert error: {str(e)}", "Low Stock Alert")


@frappe.whitelist()
def request_payment_for_order(order_name):
    """API to trigger STK Push for an order"""
    order = frappe.get_doc("Sales Order", order_name)
    
    # Verify ownership
    shop_owner = frappe.db.get_value("Shop", order.shop, "owner")
    if shop_owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw("Not authorized")

    return order.request_mpesa_payment()


@frappe.whitelist()
def get_unpaid_orders(shop=None):
    """Get all unpaid orders for dashboard"""
    filters = {"payment_status": "Unpaid", "order_status": ["!=", "Cancelled"]}
    
    if shop:
        filters["shop"] = shop
    else:
        # Only owned shops
        user_shops = frappe.get_all("Shop", filters={"owner": frappe.session.user}, pluck="name")
        filters["shop"] = ["in", user_shops]

    orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        fields=["name", "customer_name", "customer_phone", "total", "order_date", "order_source", "shop"],
        order_by="order_date desc"
    )

    return orders
