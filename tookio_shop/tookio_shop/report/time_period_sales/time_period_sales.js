// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.query_reports["Time Period Sales"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "shop",
			label: __("Shop"),
			fieldtype: "Link",
			options: "Shop",
		},
		{
			fieldname: "payment_method",
			label: __("Payment Method"),
			fieldtype: "Select",
			options: "\nMpesa\nCash\nBank",
		},
		{
			fieldname: "customer_name",
			label: __("Customer"),
			fieldtype: "Data",
		},
	]
};
