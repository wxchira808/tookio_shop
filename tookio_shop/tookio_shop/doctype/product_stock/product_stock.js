// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Stock', {
	refresh: function(frm) {
		// Hide "Sale" from the dropdown
		if (frm.fields_dict.purpose && frm.fields_dict.purpose.df.options) {
			frm.fields_dict.purpose.df.options = frm.fields_dict.purpose.df.options
				.split('\n')
				.filter(opt => opt.trim() !== "Sale")
				.join('\n');
			frm.refresh_field('purpose');
		}

		if (frm.doc.shop) {
			frm.set_query('product', 'prodcuts', function() {
				return {
					filters: {
						'shop': frm.doc.shop
					}
				};
			});
		}
	},

	shop: function(frm) {
		frm.set_query('product', 'prodcuts', function() {
			return {
				filters: {
					'shop': frm.doc.shop
				}
			};
		});
	},

	after_save: function(frm) {
		// Force refresh after submit
		if (frm.doc.docstatus === 1) {
			frm.reload_doc();
		}
	},

	fetch_products: function(frm) {
		if (!frm.doc.shop) {
			frappe.throw(__('Please select a shop first.'));
			return;
		}
		frappe.call({
			doc: frm.doc,
			method: 'fetch_products',
			freeze: true,
			callback: function(r) {
				if (r.message) {
					frm.refresh_field('prodcuts');
					frappe.show_alert({message: __('Products fetched!'), indicator: 'green'});
				}
			}
		});
	}
});
