# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PesapalPaymentLog(Document):
	def validate(self):
		"""Validate payment log"""
		if self.status == "Completed" and not self.transaction_id:
			frappe.throw("Transaction ID is required when status is Completed")
		
		if self.status == "Failed" and not self.raw_response:
			frappe.msgprint("Consider adding raw response for failed transactions", indicator="orange")
	
	def before_save(self):
		"""Set default currency if not set"""
		if not self.currency:
			self.currency = frappe.defaults.get_user_default("currency") or "KES"