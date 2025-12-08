// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pesapal Gateway Setting', {
	refresh: function(frm) {
		// Add test connection button
		if (frm.doc.enabled && frm.doc.consumer_key && frm.doc.consumer_secret) {
			frm.add_custom_button(__('Test Connection'), function() {
				frappe.call({
					method: 'tookio_shop.tookio_shop.doctype.pesapal_gateway_setting.pesapal_gateway_setting.test_pesapal_connection',
					args: {},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__('Connection test successful!'));
						}
					}
				});
			});
		}
		
		// Show notification ID
		if (frm.doc.notification_id) {
			frm.dashboard.add_comment(
				"IPN Notification ID: " + frm.doc.notification_id,
				"blue",
				true
			);
		}
	},
	
	enabled: function(frm) {
		if (frm.doc.enabled) {
			frm.set_df_property('consumer_key', 'reqd', 1);
			frm.set_df_property('consumer_secret', 'reqd', 1);
			frm.set_df_property('mode_of_payment', 'reqd', 1);
		} else {
			frm.set_df_property('consumer_key', 'reqd', 0);
			frm.set_df_property('consumer_secret', 'reqd', 0);
			frm.set_df_property('mode_of_payment', 'reqd', 0);
		}
		frm.refresh_fields();
	}
});