// Copyright (c) 2026, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tookio Stock Adjustment", {
	refresh(frm) {
		set_product_query(frm);
		recalculate_rows(frm);


		if (!frm.is_new()) {
			frm.add_custom_button(__("Apply Adjustments"), () => {
				frappe.call({
					doc: frm.doc,
					method: "apply_adjustments",
					freeze: true,
					freeze_message: __("Updating stock quantities..."),
					callback: () => {
						frm.reload_doc();
					},
				});
			});
		}
	},

	adjustment_method(frm) {
		recalculate_rows(frm);
	},

	shop(frm) {
		set_product_query(frm);
		recalculate_rows(frm);
	},

	fetch_products(frm) {
		if (!frm.doc.shop) {
			frappe.throw(__("Please select a shop first."));
			return;
		}

		frappe.call({
			doc: frm.doc,
			method: "fetch_products",
			freeze: true,
			callback: function (r) {
				if (r.message) {
					frm.refresh_field("prodcuts");
					frm.save().then(() => {
						frappe.show_alert({ message: __("Products fetched!"), indicator: "green" });
					});
				}
			},
		});
	},
});

frappe.ui.form.on("Product Stock Item", {
	product(frm, cdt, cdn) {
		recalculate_row(frm, cdt, cdn);
	},

	quantity(frm, cdt, cdn) {
		recalculate_row(frm, cdt, cdn);
	},

	current_stock(frm, cdt, cdn) {
		recalculate_row(frm, cdt, cdn);
	},
});

function set_product_query(frm) {
	if (!frm.doc.shop) {
		return;
	}

	frm.set_query("product", "prodcuts", () => ({
		filters: {
			shop: frm.doc.shop,
			enabled: 1,
		},
	}));
}

function recalculate_rows(frm) {
	(frm.doc.prodcuts || []).forEach((row) => {
		recalculate_row(frm, row.doctype, row.name);
	});
}

function recalculate_row(frm, cdt, cdn) {
	const row = locals[cdt] && locals[cdt][cdn];
	if (!row) {
		return;
	}

	const current_stock = flt(row.current_stock) || 0;
	const quantity = flt(row.quantity) || 0;
	let adjusted_stock = current_stock;

	if (frm.doc.adjustment_method === "Adjust Stock") {
		adjusted_stock = quantity;
	} else if (frm.doc.adjustment_method === "Add Stock") {
		adjusted_stock = current_stock + quantity;
	} else if (frm.doc.adjustment_method === "Remove Stock") {
		adjusted_stock = current_stock - quantity;
	}

	frappe.model.set_value(cdt, cdn, "adjusted_stock", adjusted_stock);
}
