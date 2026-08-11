import frappe
from frappe.core.doctype.user.user import User, _update_password

class CustomUser(User):
	def set_new_password(self, new_password=None):
		"""Set New Password for user without sending 'Security Alert: Your password has been changed' email"""
		if new_password and not self.flags.in_insert:
			_update_password(user=self.name, pwd=new_password, logout_all_sessions=self.logout_all_sessions)
			# Security Alert email notification intentionally suppressed to prevent false positive notifications during custom signups/role assignments.

# Monkey-patch base User class as well to guarantee suppression across all code paths
User.set_new_password = CustomUser.set_new_password
