// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shop", {
	refresh(frm) {
		// Add copy button for store link
		if (frm.doc.store_link) {
			frm.add_custom_button(__("Copy Store Link"), function() {
				frappe.utils.copy_to_clipboard(frm.doc.store_link);
				frappe.show_alert({message: __("Store link copied!"), indicator: "green"});
			});
		}
		
		// Add copy button for WhatsApp link
		if (frm.doc.whatsapp_link) {
			frm.add_custom_button(__("Copy WhatsApp Link"), function() {
				frappe.utils.copy_to_clipboard(frm.doc.whatsapp_link);
				frappe.show_alert({message: __("WhatsApp link copied!"), indicator: "green"});
			});
		}
		
		// Add button to open store in new tab
		if (frm.doc.store_link) {
			frm.add_custom_button(__("View Store"), function() {
				window.open(frm.doc.store_link, "_blank");
			});
		}
	},
});
