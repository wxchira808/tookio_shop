# Copyright (c) 2025, Tookio and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestTookioPurchase(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test shop if it doesn't exist
		if not frappe.db.exists("Shop", "Test Shop"):
			shop = frappe.get_doc({
				"doctype": "Shop",
				"shop_name": "Test Shop",
				"location": "Test Location",
				"mobile_number": "0712345678",
				"email_address": "test@shop.com"
			})
			shop.insert()
	
	def test_total_calculation(self):
		"""Test that total amount is calculated correctly"""
		purchase = frappe.get_doc({
			"doctype": "Tookio Purchase",
			"purchase_date": frappe.utils.today(),
			"shop": "Test Shop",
			"expense_category": "Stock/Inventory",
			"item_description": "Test Purchase",
			"quantity": 10,
			"unit_price": 100,
			"payment_method": "Cash",
			"payment_status": "Paid"
		})
		purchase.insert()
		
		# Check that total is calculated
		self.assertEqual(purchase.total_amount, 1000)
		
		# Clean up
		purchase.delete()
	
	def test_required_fields(self):
		"""Test that required fields are enforced"""
		purchase = frappe.get_doc({
			"doctype": "Tookio Purchase",
			"purchase_date": frappe.utils.today()
		})
		
		# Should raise error for missing required fields
		self.assertRaises(frappe.exceptions.MandatoryError, purchase.insert)
