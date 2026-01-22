# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, now


class PaymentConfirmation(Document):
	def on_update(self):
		"""When payment is verified, update user subscription"""
		if self.status == "Verified" and self.subscription_plan:
			# Get or create user subscription
			user_sub = frappe.db.exists("User Subscription", {"user": self.user})
			
			if user_sub:
				doc = frappe.get_doc("User Subscription", user_sub)
			else:
				# Set the user as session user to make them owner
				frappe.set_user(self.user)
				doc = frappe.new_doc("User Subscription")
				doc.user = self.user
			
			# Update subscription details
			doc.current_subscription = self.subscription_plan
			doc.subscription_start_date = getdate()
			doc.subscription_end_date = add_months(getdate(), 1)  # 1 month subscription
			doc.status = "Active"
			
			# Save to trigger the hooks that populate limits and history
			doc.save(ignore_permissions=True)
			
			# Reset to Administrator
			frappe.set_user("Administrator")
			
			frappe.db.commit()


def has_permission(doc, ptype, user):
	"""Custom permission: Users can only see their own payment confirmations"""
	if user == "Administrator":
		return True
	
	# Allow users to see their own payment confirmation
	if doc.user == user:
		return True
	
	return False
