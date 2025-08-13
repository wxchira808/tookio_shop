# Copyright (c) 2025, wxchira808 and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters: filters = {}
    
    # Disable prepared report features
    frappe.local.no_report_menu = True
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data, None, None, None

def get_columns():
    return [
        {
            "fieldname": "item_name",
            "label": "Item Name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "uom",
            "label": "UOM",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 100
        },
        {
            "fieldname": "stock_quantity",
            "label": "Stock Balance",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "fieldname": "price",
            "label": "Buying Price",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "selling_price",
            "label": "Selling Price",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "shop",
            "label": "Shop",
            "fieldtype": "Data",
            "width": 150
        }
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT
            p.item_name,
            p.uom,
            p.stock_quantity,
            p.price,
            p.selling_price,
            s.shop_name as shop
        FROM `tabProduct` p
        LEFT JOIN `tabShop` s ON s.name = p.shop
        WHERE p.owner = %(user)s
        AND p.docstatus = 0
        ORDER BY p.item_name ASC
    """, {"user": frappe.session.user}, as_dict=1)
