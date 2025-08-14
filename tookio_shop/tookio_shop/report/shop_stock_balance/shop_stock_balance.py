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
            "label": _("Product Name"),
            "fieldtype": "Data",
            "width": 250
        },
        {
            "fieldname": "stock_quantity",
            "label": _("Stock Quantity"),
            "fieldtype": "Float",
            "width": 150,
            "precision": 2
        },
        {
            "fieldname": "uom",
            "label": _("UOM"),
            "fieldtype": "Link",
            "options": "UOM",
            "width": 80
        },
        {
            "fieldname": "price",
            "label": _("Buying Price"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "selling_price",
            "label": _("Selling Price"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "shop",
            "label": _("Shop"),
            "fieldtype": "Link",
            "options": "Shop",
            "width": 150
        }
    ]

def get_data(filters):
    try:
        conditions = []
        values = [frappe.session.user]  # Add current user as first value
        
        if filters and filters.get("shop"):
            conditions.append("AND shop = %s")
            values.append(filters.get("shop"))

        query = """
            SELECT 
                item_name,
                stock_quantity,
                uom,
                price,
                selling_price,
                shop
            FROM 
                `tabProduct`
            WHERE 
                owner = %s
                {conditions}
            ORDER BY 
                item_name ASC
        """.format(conditions=" ".join(conditions))
        
        data = frappe.db.sql(query, values, as_dict=1)
        return data
    except Exception as e:
        return []
