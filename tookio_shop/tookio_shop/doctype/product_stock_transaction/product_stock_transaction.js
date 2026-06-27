// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Stock Transaction', {
	before_save: function(frm) {
		frm.__prompt_submit_after_save = frm.is_new() && !frm.__skip_submit_prompt_once;
	},

	refresh: function(frm) {
		// Hide "Sale" from the dropdown
		if (frm.fields_dict.purpose && frm.fields_dict.purpose.df.options) {
			frm.fields_dict.purpose.df.options = frm.fields_dict.purpose.df.options
				.split('\n')
				.filter(opt => opt.trim() !== "Sale")
				.join('\n');
			frm.refresh_field('purpose');
		}

		// Force refresh shop field to remove red outline
		if (frm.doc.shop) {
			frm.refresh_field('shop');
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
		// Refresh the shop field to remove red outline after selection
		frm.refresh_field('shop');
		
		// Clear any validation messages for the shop field
		frm.set_df_property('shop', 'reqd', 1);
		
		// Trigger validation to clear red outline
		setTimeout(() => {
			frm.validate();
		}, 100);
		
		frm.set_query('product', 'prodcuts', function() {
			return {
				filters: {
					'shop': frm.doc.shop
				}
			};
		});
	},

	after_save: function(frm) {
		const should_prompt_submit = Boolean(frm.__prompt_submit_after_save) && frm.doc.docstatus === 0;
		frm.__prompt_submit_after_save = false;
		frm.__skip_submit_prompt_once = false;

		// Force refresh after save (for both draft and submitted docs)
		frm.reload_doc().then(() => {
			// Additional refresh of shop field to ensure red outline is removed
			if (frm.doc.shop) {
				frm.refresh_field('shop');
			}

			if (should_prompt_submit) {
				frappe.confirm(
					__('Product Stock Transaction was saved as draft. Submit it now?'),
					() => frm.save('Submit')
				);
			}
		});
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
					
					// Save the document automatically after fetching products
					frm.__skip_submit_prompt_once = true;
					frm.save()
				}
			}
		});
	}
});
