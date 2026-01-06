# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.website.utils import cleanup_page_name

def get_context(context):
	"""Build context for account deletion request web form"""
	context.no_cache = 1

	# Check if user is logged in
	if not frappe.session.user or frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	# Pre-fill the user email field with current user's email
	context.user_email = frappe.session.user

	return context