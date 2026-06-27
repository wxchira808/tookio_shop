import frappe
from frappe import _


def is_system_manager():
	return "System Manager" in frappe.get_roles(frappe.session.user)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)

	columns = get_columns()
	data = get_data(filters)
	message = get_message()
	chart = get_chart(data)
	report_summary = get_report_summary(data)

	return columns, data, message, chart, report_summary


def validate_filters(filters):
	if filters.get("from_date") and filters.get("to_date") and filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be after To Date."))


def get_columns():
	return [
		{"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 110},
		{
			"fieldname": "name",
			"label": _("Invoice"),
			"fieldtype": "Link",
			"options": "Sale Invoice",
			"width": 170,
		},
		{"fieldname": "customer_name", "label": _("Customer"), "fieldtype": "Data", "width": 160},
		{"fieldname": "shop_name", "label": _("Shop"), "fieldtype": "Data", "width": 150},
		{"fieldname": "payment_method", "label": _("Payment Method"), "fieldtype": "Data", "width": 120},
		{"fieldname": "item_lines", "label": _("Item Lines"), "fieldtype": "Int", "width": 95},
		{
			"fieldname": "total_quantity",
			"label": _("Qty Sold"),
			"fieldtype": "Float",
			"precision": 2,
			"width": 100,
		},
		{"fieldname": "gross_sales", "label": _("Sales Amount"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "estimated_cost", "label": _("Estimated Cost"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "gross_profit", "label": _("Gross Profit"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "gross_margin", "label": _("Gross Margin %"), "fieldtype": "Percent", "width": 120},
	]


def get_data(filters):
	conditions = ["si.docstatus = 1"]
	values = {}

	if not is_system_manager():
		conditions.append("si.owner = %(user)s")
		values["user"] = frappe.session.user

	if filters.get("from_date"):
		conditions.append("si.posting_date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("si.posting_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.get("shop"):
		conditions.append("si.shop = %(shop)s")
		values["shop"] = filters.shop

	if filters.get("payment_method"):
		conditions.append("si.payment_method = %(payment_method)s")
		values["payment_method"] = filters.payment_method

	if filters.get("customer_name"):
		conditions.append("si.customer_name LIKE %(customer_name)s")
		values["customer_name"] = f"%{filters.customer_name}%"

	return frappe.db.sql(
		"""
		SELECT
			si.posting_date,
			si.name,
			si.customer_name,
			si.payment_method,
			shop.shop_name,
			COUNT(tsi.name) AS item_lines,
			COALESCE(SUM(tsi.quantity), 0) AS total_quantity,
			COALESCE(SUM(tsi.quantity * tsi.price), 0) AS gross_sales,
			COALESCE(SUM(tsi.quantity * IFNULL(p.price, 0)), 0) AS estimated_cost,
			COALESCE(SUM(tsi.quantity * tsi.price), 0) - COALESCE(SUM(tsi.quantity * IFNULL(p.price, 0)), 0) AS gross_profit,
			CASE
				WHEN COALESCE(SUM(tsi.quantity * tsi.price), 0) = 0 THEN 0
				ELSE (
					(COALESCE(SUM(tsi.quantity * tsi.price), 0) - COALESCE(SUM(tsi.quantity * IFNULL(p.price, 0)), 0))
					/ COALESCE(SUM(tsi.quantity * tsi.price), 0)
				) * 100
			END AS gross_margin
		FROM `tabSale Invoice` si
		LEFT JOIN `tabTookio Sales Invoice Item` tsi
			ON tsi.parent = si.name
		LEFT JOIN `tabProduct` p
			ON p.name = tsi.product
		LEFT JOIN `tabShop` shop
			ON shop.name = si.shop
		WHERE {conditions}
		GROUP BY si.name
		ORDER BY si.posting_date DESC, si.creation DESC
		""".format(conditions=" AND ".join(conditions)),
		values,
		as_dict=1,
	)


def get_chart(data):
	if not data:
		return None

	daily_totals = {}
	for row in data:
		label = str(row.posting_date)
		if label not in daily_totals:
			daily_totals[label] = {"sales": 0, "profit": 0}
		daily_totals[label]["sales"] += row.gross_sales or 0
		daily_totals[label]["profit"] += row.gross_profit or 0

	labels = sorted(daily_totals.keys())[-12:]
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Sales"), "values": [daily_totals[label]["sales"] for label in labels]},
				{"name": _("Gross Profit"), "values": [daily_totals[label]["profit"] for label in labels]},
			],
		},
		"type": "line",
		"colors": ["#1f7a8c", "#c75c5c"],
	}


def get_report_summary(data):
	total_sales = sum((row.gross_sales or 0) for row in data)
	total_cost = sum((row.estimated_cost or 0) for row in data)
	total_profit = total_sales - total_cost
	total_quantity = sum((row.total_quantity or 0) for row in data)
	invoice_count = len(data)
	average_invoice_value = total_sales / invoice_count if invoice_count else 0
	margin = (total_profit / total_sales * 100) if total_sales else 0

	return [
		{"value": total_sales, "label": _("Total Sales"), "indicator": "Blue", "datatype": "Currency"},
		{
			"value": total_profit,
			"label": _("Gross Profit"),
			"indicator": "Green" if total_profit >= 0 else "Red",
			"datatype": "Currency",
		},
		{"value": total_quantity, "label": _("Units Sold"), "indicator": "Orange", "datatype": "Float"},
		{
			"value": average_invoice_value,
			"label": _("Average Invoice"),
			"indicator": "Purple",
			"datatype": "Currency",
		},
		{
			"value": margin,
			"label": _("Gross Margin"),
			"indicator": "Green" if margin >= 0 else "Red",
			"datatype": "Percent",
		},
		{"value": invoice_count, "label": _("Invoices"), "indicator": "Gray", "datatype": "Int"},
	]


def get_message():
	return _(
		"Estimated Cost and Gross Profit use each product's current Buying Price field, not a historical cost snapshot."
	)
