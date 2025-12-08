# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProductStockItem(Document):
	def validate(self):
		"""Validate that product is enabled for stock transactions"""
		if self.product:
			is_enabled = frappe.db.get_value('Product', self.product, 'enabled')
			if not is_enabled:
				frappe.throw(f"Product {self.product} is disabled and cannot be used in stock transactions.")
