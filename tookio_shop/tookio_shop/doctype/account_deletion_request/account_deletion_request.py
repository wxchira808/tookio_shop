# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AccountDeletionRequest(Document):
	def before_insert(self):
		"""Auto-fill submission details"""
		if not self.submitted_by:
			self.submitted_by = frappe.session.user
		if not self.submission_date:
			self.submission_date = frappe.utils.now_datetime()

	def validate(self):
		"""Validate the request"""
		# Ensure the user_email matches a valid user
		if self.user_email:
			user_exists = frappe.db.exists("User", self.user_email)
			if not user_exists:
				frappe.throw(f"User '{self.user_email}' does not exist in the system")

		# Ensure the submitted_by matches the current user (prevent impersonation)
		if self.submitted_by != frappe.session.user:
			frappe.throw("You can only submit requests for your own account")

	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("status"):
			if self.status == "Completed":
				# Log completion
				frappe.logger().info(f"Account deletion request {self.name} marked as completed")
			elif self.status == "Approved":
				# Send notification to user
				self.notify_user("approved")
			elif self.status == "Rejected":
				# Send notification to user
				self.notify_user("rejected")

	def notify_user(self, action):
		"""Send notification to user about request status"""
		try:
			subject = f"Account Deletion Request {action.title()}"
			message = f"""
			Your account deletion request has been {action}.

			Request Details:
			- Username/Email: {self.user_email}
			- Submission Date: {self.submission_date}

			"""
			if self.admin_notes:
				message += f"Admin Notes: {self.admin_notes}\n\n"

			if action == "approved":
				message += "Your account will be deleted within 24-48 hours. You will receive a confirmation email once the deletion is complete."
			elif action == "rejected":
				message += "If you have any questions about this decision, please contact our support team."

			frappe.sendmail(
				recipients=[self.user_email],
				subject=subject,
				message=message
			)
		except Exception as e:
			frappe.log_error(f"Failed to send notification for account deletion request {self.name}: {str(e)}")