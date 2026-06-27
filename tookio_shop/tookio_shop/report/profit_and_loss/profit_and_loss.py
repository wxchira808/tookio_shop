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
		{"fieldname": "period", "label": _("Period"), "fieldtype": "Data", "width": 120},
		{"fieldname": "sales_revenue", "label": _("Sales Revenue"), "fieldtype": "Currency", "width": 140},
		{
			"fieldname": "cost_of_goods_sold",
			"label": _("Cost of Goods Sold"),
			"fieldtype": "Currency",
			"width": 160,
		},
		{"fieldname": "gross_profit", "label": _("Gross Profit"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "operating_expenses", "label": _("Expenses"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "net_profit", "label": _("Net Profit / Loss"), "fieldtype": "Currency", "width": 150},
		{"fieldname": "gross_margin", "label": _("Gross Margin %"), "fieldtype": "Percent", "width": 120},
		{"fieldname": "net_margin", "label": _("Net Margin %"), "fieldtype": "Percent", "width": 120},
	]


def get_data(filters):
	sales_map = get_sales_map(filters)
	expense_map = get_expense_map(filters)
	all_periods = sorted(set(sales_map) | set(expense_map))

	data = []
	for period in all_periods:
		sales_revenue = sales_map.get(period, {}).get("sales_revenue", 0)
		cost_of_goods_sold = sales_map.get(period, {}).get("cost_of_goods_sold", 0)
		operating_expenses = expense_map.get(period, 0)
		gross_profit = sales_revenue - cost_of_goods_sold
		net_profit = gross_profit - operating_expenses

		data.append(
			{
				"period": period,
				"sales_revenue": sales_revenue,
				"cost_of_goods_sold": cost_of_goods_sold,
				"gross_profit": gross_profit,
				"operating_expenses": operating_expenses,
				"net_profit": net_profit,
				"gross_margin": (gross_profit / sales_revenue * 100) if sales_revenue else 0,
				"net_margin": (net_profit / sales_revenue * 100) if sales_revenue else 0,
			}
		)

	return data


def get_sales_map(filters):
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

	period_expression = get_period_expression("si.posting_date", filters.get("periodicity"))

	rows = frappe.db.sql(
		"""
		SELECT
			{period_expression} AS period,
			COALESCE(SUM(tsi.quantity * tsi.price), 0) AS sales_revenue,
			COALESCE(SUM(tsi.quantity * IFNULL(p.price, 0)), 0) AS cost_of_goods_sold
		FROM `tabSale Invoice` si
		LEFT JOIN `tabTookio Sales Invoice Item` tsi
			ON tsi.parent = si.name
		LEFT JOIN `tabProduct` p
			ON p.name = tsi.product
		WHERE {conditions}
		GROUP BY period
		ORDER BY MIN(si.posting_date) ASC
		""".format(
			period_expression=period_expression,
			conditions=" AND ".join(conditions),
		),
		values,
		as_dict=1,
	)

	return {
		row.period: {
			"sales_revenue": row.sales_revenue or 0,
			"cost_of_goods_sold": row.cost_of_goods_sold or 0,
		}
		for row in rows
	}


def get_expense_map(filters):
	conditions = ["1 = 1"]
	values = {}

	if not is_system_manager():
		conditions.append("tp.owner = %(user)s")
		values["user"] = frappe.session.user

	if filters.get("from_date"):
		conditions.append("tp.date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("tp.date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.get("shop"):
		conditions.append("tp.shop = %(shop)s")
		values["shop"] = filters.shop

	period_expression = get_period_expression("tp.date", filters.get("periodicity"))

	rows = frappe.db.sql(
		"""
		SELECT
			{period_expression} AS period,
			COALESCE(SUM(tp.amount), 0) AS operating_expenses
		FROM `tabTookio Purchase` tp
		WHERE {conditions}
		GROUP BY period
		ORDER BY MIN(tp.date) ASC
		""".format(
			period_expression=period_expression,
			conditions=" AND ".join(conditions),
		),
		values,
		as_dict=1,
	)

	return {row.period: row.operating_expenses or 0 for row in rows}


def get_period_expression(date_field, periodicity):
	periodicity = periodicity or "Monthly"

	if periodicity == "Daily":
		return "DATE_FORMAT({0}, '%%Y-%%m-%%d')".format(date_field)
	if periodicity == "Summary":
		return "'Overall'"
	return "DATE_FORMAT({0}, '%%Y-%%m')".format(date_field)


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [row["period"] for row in data],
			"datasets": [
				{"name": _("Sales"), "values": [row["sales_revenue"] for row in data]},
				{"name": _("Expenses"), "values": [row["operating_expenses"] for row in data]},
				{"name": _("Net Profit / Loss"), "values": [row["net_profit"] for row in data]},
			],
		},
		"type": "bar",
		"colors": ["#1f7a8c", "#f0b429", "#3d9970"],
	}


def get_report_summary(data):
	total_sales = sum((row["sales_revenue"] or 0) for row in data)
	total_gross_profit = sum((row["gross_profit"] or 0) for row in data)
	total_expenses = sum((row["operating_expenses"] or 0) for row in data)
	total_net_profit = sum((row["net_profit"] or 0) for row in data)

	return [
		{"value": total_sales, "label": _("Sales Revenue"), "indicator": "Blue", "datatype": "Currency"},
		{
			"value": total_gross_profit,
			"label": _("Gross Profit"),
			"indicator": "Green" if total_gross_profit >= 0 else "Red",
			"datatype": "Currency",
		},
		{"value": total_expenses, "label": _("Expenses"), "indicator": "Orange", "datatype": "Currency"},
		{
			"value": total_net_profit,
			"label": _("Net Profit / Loss"),
			"indicator": "Green" if total_net_profit >= 0 else "Red",
			"datatype": "Currency",
		},
	]


def get_message():
	return _(
		"Cost of Goods Sold is estimated from each product's current Buying Price. Expenses are pulled from Tookio Purchase entries."
	)
