// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Product", {
	setup(frm) {
		frm.set_query("item_group", () => ({
			filters: { shop: frm.doc.shop, enabled: 1 },
		}));
	},
	shop(frm) {
		if (frm.doc.item_group) {
			frm.set_value("item_group", null);
		}
	},
});
