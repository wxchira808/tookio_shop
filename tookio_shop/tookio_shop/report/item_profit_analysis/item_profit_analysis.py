import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "month",
            "label": _("Month"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "total_sales",
            "label": _("Total Sales"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "total_cost",
            "label": _("Total Cost"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "total_profit",
            "label": _("Total Profit"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "profit_margin",
            "label": _("Profit Margin %"),
            "fieldtype": "Percent",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = []
    values = [frappe.session.user]  # Add current user as first value
    
    if filters and filters.get("from_date"):
        conditions.append("AND si.posting_date >= %s")
        values.append(filters.get("from_date"))
    
    if filters and filters.get("to_date"):
        conditions.append("AND si.posting_date <= %s")
        values.append(filters.get("to_date"))
    
    if filters and filters.get("shop"):
        conditions.append("AND si.shop = %s")
        values.append(filters.get("shop"))

    data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(si.posting_date, '%%Y-%%m') as month,
            SUM(tsi.price * tsi.quantity) as total_sales,
            SUM(p.price * tsi.quantity) as total_cost,
            SUM((tsi.price - p.price) * tsi.quantity) as total_profit,
            (SUM((tsi.price - p.price) * tsi.quantity) / NULLIF(SUM(tsi.price * tsi.quantity), 0)) * 100 as profit_margin
        FROM 
            `tabSale Invoice` si
        INNER JOIN
            `tabTookio Sales Invoice Item` tsi ON tsi.parent = si.name
        INNER JOIN
            `tabProduct` p ON p.name = tsi.product
        WHERE 
            si.docstatus = 1
            AND si.owner = %s
            {conditions}
        GROUP BY 
            month
        ORDER BY 
            month DESC
    """.format(
        conditions=" ".join(conditions)
    ), values, as_dict=1)

    return data
