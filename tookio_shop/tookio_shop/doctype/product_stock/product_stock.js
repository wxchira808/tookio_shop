// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Stock', {
	after_save: function(frm) {
		// Force refresh after submit
		if (frm.doc.docstatus === 1) {
			frm.reload_doc();
		}
	}
});

frappe.ui.form.on('Product Stock', {
    refresh: function(frm) {
        // Hide "Sale" from the dropdown
        frm.fields_dict.purpose.df.options = frm.fields_dict.purpose.df.options
            .split('\n')
            .filter(opt => opt.trim() !== "Sale")
            .join('\n');
        frm.refresh_field('purpose');
    }
});
// Additional existing code can follow here
// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt


frappe.ui.form.on('Product Stock', {
	fetch_products: function(frm) {
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
