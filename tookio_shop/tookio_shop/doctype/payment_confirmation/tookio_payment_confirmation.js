// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tookio Payment Confirmation", {
	refresh(frm) {
		if (frm.doc.status === "Pending Verification") {
			frm.add_custom_button(__("Verify Payment"), function() {
				frm.set_value("status", "Verified");
				frm.set_value("verified_by", frappe.session.user);
				frm.set_value("verified_date", frappe.datetime.now_datetime());
				frm.save();
			});
			
			frm.add_custom_button(__("Reject Payment"), function() {
				frm.set_value("status", "Rejected");
				frm.set_value("verified_by", frappe.session.user);
				frm.set_value("verified_date", frappe.datetime.now_datetime());
				frm.save();
			});
		}
	},
});
