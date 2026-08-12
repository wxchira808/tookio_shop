# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Shop(Document):
	def on_update(self):
		if not self.enabled:
			frappe.db.set_value("Tookio Website", {"shop": self.name}, "enabled", 0, update_modified=False)

	def on_trash(self):
		frappe.db.set_value("Tookio Website", {"shop": self.name}, "enabled", 0, update_modified=False)
