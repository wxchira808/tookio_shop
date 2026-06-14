// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sale Invoice", {
	before_save(frm) {
		frm.__prompt_submit_after_save = frm.is_new();
	},
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
	after_save(frm) {
		if (!frm.__prompt_submit_after_save || frm.doc.docstatus !== 0) {
			frm.__prompt_submit_after_save = false;
			return;
		}

		frm.__prompt_submit_after_save = false;

		frappe.confirm(
			__("Sale Invoice was saved as draft. Submit it now?"),
			() => frm.save("Submit")
		);
	},
});
