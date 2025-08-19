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
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "name",
            "label": _("Invoice Number"),
            "fieldtype": "Link",
            "options": "Sale Invoice",
            "width": 180
        },
        {
            "fieldname": "customer_name",
            "label": _("Customer"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "payment_method",
            "label": _("Payment Method"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "shop_name",
            "label": _("Shop"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "total",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = []
    values = [frappe.session.user]  # Add current user as first value
    
    if filters.get("from_date"):
        conditions.append("AND si.posting_date >= %s")
        values.append(filters.get("from_date"))
    
    if filters.get("to_date"):
        conditions.append("AND si.posting_date <= %s")
        values.append(filters.get("to_date"))
    
    if filters.get("shop"):
        conditions.append("AND si.shop = %s")
        values.append(filters.get("shop"))
    
    if filters.get("payment_method"):
        conditions.append("AND si.payment_method = %s")
        values.append(filters.get("payment_method"))

    data = frappe.db.sql("""
        SELECT
            si.posting_date,
            si.name,
            si.customer_name,
            si.payment_method,
            s.shop_name as shop_name,
            si.total
        FROM
            `tabSale Invoice` si
        LEFT JOIN `tabShop` s ON s.name = si.shop
        WHERE
            si.docstatus = 1
            AND si.owner = %s
            {conditions}
        ORDER BY
            posting_date DESC
    """.format(
        conditions=" ".join(conditions)
    ), values, as_dict=1)

    return data
