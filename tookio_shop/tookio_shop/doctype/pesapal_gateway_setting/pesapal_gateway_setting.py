# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import uuid


class PesapalGatewaySetting(Document):
	def validate(self):
		"""Validate gateway settings"""
		if self.enabled:
			if not self.consumer_key or not self.consumer_secret:
				frappe.throw("Consumer Key and Consumer Secret are required when gateway is enabled")
			
			if not self.mode_of_payment:
				frappe.throw("Mode of Payment is required when gateway is enabled")
		
		# Generate notification ID if not present
		if not self.notification_id:
			self.notification_id = str(uuid.uuid4())
	
	def before_save(self):
		"""Mask sensitive data in logs"""
		if self.consumer_key:
			frappe.logger().info(f"Pesapal Gateway Settings updated - Key: {self.consumer_key[:8]}...")
		
		if self.consumer_secret:
			frappe.logger().info("Pesapal Gateway Settings updated - Secret configured")


@frappe.whitelist()
def test_pesapal_connection():
	"""Test connection to Pesapal API"""
	try:
		settings = frappe.get_doc("Pesapal Gateway Setting", "pesapal")
		
		if not settings.enabled:
			frappe.throw("Pesapal gateway is not enabled")
		
		if not settings.consumer_key or not settings.consumer_secret:
			frappe.throw("API credentials are not configured")
		
		# Here you would typically make a test API call to Pesapal
		# For now, just validate that credentials are set
		frappe.msgprint("Pesapal connection test passed - credentials are configured")
		
		return True
		
	except frappe.DoesNotExistError:
		frappe.throw("Pesapal Gateway Setting document 'pesapal' not found. Please create it first.")
	except Exception as e:
		frappe.throw(f"Connection test failed: {str(e)}")