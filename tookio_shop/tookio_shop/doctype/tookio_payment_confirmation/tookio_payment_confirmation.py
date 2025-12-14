# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, now


class TookioPaymentConfirmation(Document):
	def on_update(self):
		"""When payment is verified, update user subscription"""
		if self.status == "Verified" and self.subscription_plan:
			# Get or create user subscription
			user_sub = frappe.db.exists("Tookio User Subscription", {"user": self.user})
			
			if user_sub:
				doc = frappe.get_doc("Tookio User Subscription", user_sub)
			else:
				doc = frappe.new_doc("Tookio User Subscription")
				doc.user = self.user
			
			# Update subscription details
			doc.current_subscription = self.subscription_plan
			doc.subscription_start_date = getdate()
			doc.subscription_end_date = add_months(getdate(), 1)  # 1 month subscription
			doc.status = "Active"
			
			# Save to trigger the hooks that populate limits and history
			doc.save(ignore_permissions=True)
			
			frappe.db.commit()
