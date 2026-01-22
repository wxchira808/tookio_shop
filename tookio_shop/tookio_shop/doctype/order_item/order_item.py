# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OrderItem(Document):
	def validate(self):
		"""Validate that product is enabled"""
		if self.product:
			is_enabled = frappe.db.get_value('Product', self.product, 'enabled')
			if not is_enabled:
				frappe.throw(f"Product {self.product} is disabled and cannot be used in sales invoices.")

	@frappe.whitelist()
	def filter_enabled_products(self, query=None):
		"""Filter to show only enabled products in link field"""
		return frappe.get_list('Product', 
			filters={'enabled': 1},
			fields=['name', 'item_name', 'selling_price'],
			limit_page_length=500)
