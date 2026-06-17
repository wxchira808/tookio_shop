// Copyright (c) 2026, Tookio and contributors
// For license information, please see license.txt

frappe.query_reports["Profit And Loss"] = {
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
			fieldname: "periodicity",
			label: __("Periodicity"),
			fieldtype: "Select",
			options: "Summary\nMonthly\nDaily",
			default: "Monthly",
		},
	],
};
