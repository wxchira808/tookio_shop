#!/usr/bin/env python3
"""
Script to create default Tookio subscription plans
Run this after doctypes are installed on the live site
"""

import frappe
from frappe.utils import getdate, add_months

def create_subscription_plans():
    """Create the three default subscription plans"""
    
    plans = [
        {
            "subscription_name": "Free Plan",
            "description": "Perfect for getting started with basic shop management",
            "price": 0,
            "currency": "KES",
            "shop_limit": 1,
            "products_limit": 50,
            "sales_invoice_limit": 200,
            "enabled": 1
        },
        {
            "subscription_name": "Starter Plan",
            "description": "Great for growing businesses with unlimited sales",
            "price": 500,
            "currency": "KES",
            "shop_limit": 1,
            "products_limit": 150,
            "sales_invoice_limit": 0,  # 0 means unlimited
            "enabled": 1
        },
        {
            "subscription_name": "Premium Plan",
            "description": "For serious businesses with multiple shops and unlimited features",
            "price": 1500,
            "currency": "KES",
            "shop_limit": 5,
            "products_limit": 400,
            "sales_invoice_limit": 0,  # 0 means unlimited
            "enabled": 1
        }
    ]
    
    for plan in plans:
        # Check if plan already exists
        if not frappe.db.exists("Tookio Subscription", {"subscription_name": plan["subscription_name"]}):
            doc = frappe.new_doc("Tookio Subscription")
            doc.update(plan)
            doc.insert(ignore_permissions=True)
            print(f"Created plan: {plan['subscription_name']}")
        else:
            print(f"Plan already exists: {plan['subscription_name']}")
    
    frappe.db.commit()
    print("Subscription plans created successfully!")

if __name__ == "__main__":
    # This should be run from bench console or as a frappe script
    create_subscription_plans()
