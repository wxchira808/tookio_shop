// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sale Invoice", {
	refresh(frm) {
		if (frm.doc.shop) {
			frm.set_query("product", "items", function () {
				return {
					filters: {
						shop: frm.doc.shop,
					},
				};
			});
		}
	},
	shop(frm) {
		frm.clear_table("items");
		frm.refresh_field("items");
		if (frm.doc.shop) {
			frm.set_query("product", "items", function () {
				return {
					filters: {
						shop: frm.doc.shop,
					},
				};
			});
		}
	},
});
