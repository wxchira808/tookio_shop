// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sale Invoice", {
	calculate_total(frm) {
		const total = (frm.doc.items || []).reduce((sum, item) => {
			const quantity = flt(item.quantity);
			const price = flt(item.price);
			return sum + quantity * price;
		}, 0);

		frm.set_value("total", total);
	},

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

		frm.trigger("calculate_total");
	},
	shop(frm) {
		frm.clear_table("items");
		frm.refresh_field("items");
		frm.trigger("calculate_total");
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

	items_add(frm) {
		frm.trigger("calculate_total");
	},

	items_remove(frm) {
		frm.trigger("calculate_total");
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

frappe.ui.form.on("Tookio Sales Invoice Item", {
	quantity(frm) {
		frm.trigger("calculate_total");
	},

	price(frm) {
		frm.trigger("calculate_total");
	},

	items_remove(frm) {
		frm.trigger("calculate_total");
	},
});
