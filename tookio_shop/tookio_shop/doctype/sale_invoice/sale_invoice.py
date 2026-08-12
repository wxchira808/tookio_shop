# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class SaleInvoice(Document):
	def validate(self):
		self.currency = _get_shop_currency(self.shop)
		# Check that all products are enabled
		for item in self.items:
			if item.product:
				is_enabled = frappe.db.get_value('Product', item.product, 'enabled')
				if not is_enabled:
					frappe.throw(f"Product {item.product} is disabled and cannot be added to sales invoices.")
		
		total = 0
		for item in self.items:
			if item.price and item.quantity:
				total += item.price * item.quantity
		self.total = total

	def on_submit(self):
		# Create a Product Stock Transaction entry for this sale
		product_stock = frappe.new_doc("Product Stock Transaction")
		product_stock.purpose = "Sale"
		product_stock.date = self.get("date")
		product_stock.shop = self.get("shop")
		product_stock.prodcuts = []
		for item in self.items:
			if item.product and item.quantity:
				product_stock.append("prodcuts", {
					"product": item.product,
					"quantity": item.quantity,
					"uom": getattr(item, "uom", None),
					"product_name": getattr(item, "item_name", None),
					"current_stock": frappe.db.get_value("Product", item.product, "stock_quantity")
				})
		product_stock.flags.ignore_permissions = True
		product_stock.insert()
		product_stock.submit()

	def on_cancel(self):
		# Restore stock in Product doctype for each item
		for item in self.items:
			if item.price and item.quantity:
				frappe.db.sql(
					"""
					UPDATE `tabProduct`
					SET stock_quantity = stock_quantity + %s
					WHERE name = %s
					""",
					(item.quantity, item.product)
				)

	def no_stock(self):
		low_stock_items = []
		for item in self.items:
			if item.stock < item.quantity or item.stock <= 0:
				low_stock_items.append(
					_("{product}: In stock {stock}, requested {quantity}").format(
						product=item.product, stock=item.stock, quantity=item.quantity
					)
				)
		if low_stock_items:
			frappe.throw(_("Low stock for the following items:<br>{0}").format("<br>".join(low_stock_items)))


def _get_shop_currency(shop):
	currency = frappe.db.get_value("Shop", shop, "currency")
	if not currency:
		frappe.throw("Set a currency on this shop before creating or editing sales invoices.")
	return currency
