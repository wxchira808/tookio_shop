# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document



import frappe


class ProductStock(Document):
	def on_submit(self):
		messages = []
		for item in self.prodcuts:
			if not item.product or not item.quantity:
				continue
			product_name = item.product_name or frappe.db.get_value("Product", item.product, "item_name") or item.product
			if self.purpose == "Add Stock":
				frappe.db.sql("""
					UPDATE `tabProduct`
					SET stock_quantity = stock_quantity + %s
					WHERE name = %s
				""", (item.quantity, item.product))
				messages.append(f"Added {item.quantity} to {product_name}")
			elif self.purpose == "Remove Stock" or self.purpose == "Sale":
				# Both Remove Stock and Sale deduct stock
				current_stock = frappe.db.get_value("Product", item.product, "stock_quantity") or 0
				if item.quantity > current_stock:
					frappe.throw(f"Cannot remove {item.quantity} from {product_name}. Only {current_stock} in stock.")
				frappe.db.sql("""
					UPDATE `tabProduct`
					SET stock_quantity = stock_quantity - %s
					WHERE name = %s
				""", (item.quantity, item.product))
				if self.purpose == "Remove Stock":
					messages.append(f"Removed {item.quantity} from {product_name}")
				else:
					messages.append(f"Sale: Removed {item.quantity} from {product_name}")
			elif self.purpose == "Adjust Stock":
				frappe.db.set_value("Product", item.product, "stock_quantity", item.quantity)
				messages.append(f"Set {product_name} stock to {item.quantity}")
		if messages:
			frappe.msgprint("<br>".join(messages), title="Stock Update Summary")

	@frappe.whitelist()
	def fetch_products(self):
		"""
		Fetch all Products for the selected shop and populate the 'prodcuts' child table.
		"""
		# Clear existing items
		self.set('prodcuts', [])
		if not self.shop:
			frappe.throw(_('Please select a shop first.'))
		products = frappe.get_all(
			'Product',
			fields=['name', 'uom', 'stock_quantity'],
			filters={'shop': self.shop}
		)
		for prod in products:
			self.append('prodcuts', {
				'product': prod['name'],
				'uom': prod.get('uom', ''),
				'current_stock': prod.get('stock_quantity', 0),
				'quantity': 0
			})
		return [d.as_dict() for d in self.prodcuts]
