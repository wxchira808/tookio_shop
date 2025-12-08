# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Product(Document):
	def before_validate(self):
		"""Ensure enabled field has a default value"""
		if self.enabled is None:
			self.enabled = 1

	@staticmethod
	@frappe.whitelist()
	def get_enabled_products(shop=None, filters=None):
		"""Get only enabled products, optionally filtered by shop"""
		if filters is None:
			filters = {}
		
		filters['enabled'] = 1
		
		if shop:
			filters['shop'] = shop
		
		return frappe.get_list('Product', filters=filters, fields=['name', 'item_name', 'selling_price', 'stock_quantity', 'shop'])
