# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Product(Document):
	def before_validate(self):
		"""Ensure enabled field has a default value"""
		if self.enabled is None:
			self.enabled = 1
		if self.shop:
			self.currency = _get_shop_currency(self.shop)
		if self.item_group:
			group_shop = frappe.db.get_value("Tookio Item Group", self.item_group, "shop")
			if group_shop != self.shop:
				frappe.throw("The selected item group belongs to a different shop.")
		if self.track_stock and flt(self.stock_quantity) < 0:
			frappe.throw(_("Stock quantity cannot be negative for a product that tracks stock."))


def _get_shop_currency(shop):
	currency = frappe.db.get_value("Shop", shop, "currency")
	if not currency:
		frappe.throw("Set a currency on this shop before creating or editing products.")
	return currency

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
