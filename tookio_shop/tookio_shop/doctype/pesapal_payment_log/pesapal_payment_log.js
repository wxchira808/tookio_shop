// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pesapal Payment Log', {
	refresh: function(frm) {
		// Add custom buttons for payment actions
		if (frm.doc.status === 'Pending') {
			frm.add_custom_button(__('Mark Completed'), function() {
				frm.set_value('status', 'Completed');
				frm.save();
			});
			
			frm.add_custom_button(__('Mark Failed'), function() {
				frm.set_value('status', 'Failed');
				frm.save();
			});
		}
		
		// Show raw response in a formatted way
		if (frm.doc.raw_response) {
			try {
				let response = JSON.parse(frm.doc.raw_response);
				frm.dashboard.add_comment(
					"Raw Response: " + JSON.stringify(response, null, 2),
					"blue",
					true
				);
			} catch (e) {
				// Not JSON, show as text
			}
		}
	},
	
	status: function(frm) {
		// Auto-set transaction ID if status changes to completed
		if (frm.doc.status === 'Completed' && !frm.doc.transaction_id) {
			frm.set_value('transaction_id', 'TXN-' + frm.doc.reference);
		}
	}
});