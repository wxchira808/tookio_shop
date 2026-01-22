# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Shop(Document):
	def validate(self):
		"""Generate store links when shop is created or updated"""
		self.generate_store_links()
	
	def generate_store_links(self):
		"""Generate shareable links for the shop"""
		if self.name:
			# Get the base URL from site config
			base_url = frappe.utils.get_url()
			
			# Store link for TikTok/Instagram bio
			self.store_link = f"{base_url}/store?shop={self.name}"
			
			# WhatsApp link - opens chat with store link
			self.whatsapp_link = f"https://wa.me/?text={self.store_link}"
