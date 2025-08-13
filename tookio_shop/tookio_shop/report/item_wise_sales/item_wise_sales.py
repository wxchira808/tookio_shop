import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "total_quantity",
            "label": _("Total Quantity Sold"),
            "fieldtype": "Float",
            "width": 150
        },
        {
            "fieldname": "total_amount",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "avg_rate",
            "label": _("Average Selling Rate"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "total_quantity",
            "label": _("Total Quantity Sold"),
            "fieldtype": "Float",
            "width": 150
        },
        {
            "fieldname": "total_amount",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "avg_rate",
            "label": _("Average Selling Rate"),
            "fieldtype": "Currency",
            "width": 150
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
            p.item_name,
            SUM(tsi.quantity) as total_quantity,
            SUM(tsi.price * tsi.quantity) as total_amount,
            AVG(tsi.price) as avg_rate
        FROM 
            `tabTookio Sales Invoice Item` tsi
        LEFT JOIN
            `tabProduct` p ON p.name = tsi.product
        INNER JOIN 
            `tabSale Invoice` si ON si.name = tsi.parent
        WHERE 
            si.docstatus = 1
            AND si.owner = %s
            {conditions}
        GROUP BY 
            tsi.product
        ORDER BY 
            total_amount DESC
    """.format(
        conditions=" ".join(conditions)
    ), values, as_dict=1)

    return data

def get_conditions(filters):
    conditions = ["si.owner = %(user)s"]  # Always filter by current user
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
    if filters.get("shop"):
        conditions.append("si.shop = %(shop)s")

    return " AND " + " AND ".join(conditions)
