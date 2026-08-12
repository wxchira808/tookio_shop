# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TookioPurchase(Document):
	def validate(self):
		self.currency = frappe.db.get_value("Shop", self.shop, "currency")
		if not self.currency:
			frappe.throw(_("Set a currency on this shop before creating or editing purchases."))
