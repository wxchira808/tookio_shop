frappe.ready(function() {
	// Pre-fill user email field
	if (frappe.web_form && frappe.web_form.doc) {
		frappe.web_form.set_value('user_email', frappe.session.user);
	}
})