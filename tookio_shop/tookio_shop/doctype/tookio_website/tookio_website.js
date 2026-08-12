frappe.ui.form.on("Tookio Website", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.website_slug) {
			frm.add_web_link(`/shop/${frm.doc.website_slug}`, __("Open Storefront"));
		}
	},
});
