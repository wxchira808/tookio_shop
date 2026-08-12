# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, today


class TookioUserSubscription(Document):
	def before_save(self):
		"""Mirror the selected plan for display; enforcement always reads the plan itself."""
		if not self.current_subscription:
			return

		subscription = frappe.get_doc("Tookio Subscription", self.current_subscription)
		self.shop_limit = subscription.shop_limit
		self.products_limit = subscription.products_limit
		self.sales_invoice_limit = subscription.sales_invoice_limit
		self.website_enabled = subscription.website_enabled
		self.website_limit = subscription.website_limit

		if subscription.subscription_name == "Free Plan":
			self.subscription_end_date = None
	
	def on_update(self):
		"""Add to history when subscription changes"""
		# Check if this is a new subscription or subscription change
		if self.current_subscription and self.subscription_start_date:
			# Check if this entry already exists in history
			existing = False
			for row in self.subscription_history:
				if row.subscription_start_date == self.subscription_start_date and row.tookio_subscription == self.current_subscription:
					existing = True
					break
			
			# If not in history, add it
			if not existing:
				self.append("subscription_history", {
					"tookio_subscription": self.current_subscription,
					"subscription_start_date": self.subscription_start_date,
					"subscription_end_date": self.subscription_end_date,
					"status": self.status
				})
				self.save()
		
		# Log subscription status changes
		frappe.logger().info(f"📋 Subscription updated for {self.user}: {self.current_subscription} (Status: {self.status})")


def has_permission(doc, ptype, user):
	"""Custom permission: Users can only see their own subscription"""
	if user == "Administrator":
		return True
	
	# Allow users to see their own subscription record
	if doc.user == user:
		return True
	
	return False
