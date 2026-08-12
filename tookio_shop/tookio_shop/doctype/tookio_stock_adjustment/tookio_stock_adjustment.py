# Copyright (c) 2026, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class TookioStockAdjustment(Document):
	def validate(self):
		self._validate_adjustment_method()
		self._validate_products()

	def _validate_adjustment_method(self):
		if self.adjustment_method not in {"Adjust Stock", "Add Stock", "Remove Stock"}:
			frappe.throw(_("Please select a valid adjustment method."))

	def _validate_products(self):
		for item in self.prodcuts or []:
			if not item.product:
				continue

			product = frappe.db.get_value(
				"Product", item.product, ["enabled", "track_stock", "shop"], as_dict=True
			)
			if not product or not product.enabled:
				frappe.throw(
					_("Product {0} is disabled and cannot be used in stock adjustments.").format(item.product)
				)
			if product.shop != self.shop:
				frappe.throw(_("Product {0} belongs to a different shop.").format(item.product))
			if not product.track_stock:
				frappe.throw(_("Product {0} does not track stock.").format(item.product))

			if item.quantity is None:
				frappe.throw(_("Please enter a quantity for product {0}.").format(item.product))

			quantity = flt(item.quantity)
			if quantity < 0:
				frappe.throw(_("Quantity for product {0} cannot be negative.").format(item.product))

			if self.adjustment_method == "Remove Stock":
				current_stock = flt(frappe.db.get_value("Product", item.product, "stock_quantity") or 0)
				if quantity > current_stock:
					frappe.throw(
						_("Cannot remove {0} from product {1}. Only {2} in stock.").format(
							quantity,
							item.product,
							current_stock,
						)
					)

	def _calculate_adjusted_stock(self, current_stock, quantity):
		current_stock = flt(current_stock)
		quantity = flt(quantity)
		if self.adjustment_method == "Adjust Stock":
			return quantity
		if self.adjustment_method == "Add Stock":
			return current_stock + quantity
		if self.adjustment_method == "Remove Stock":
			return current_stock - quantity
		return current_stock

	@frappe.whitelist()
	def fetch_products(self):
		self.set("prodcuts", [])

		if not self.shop:
			frappe.throw(_("Please select a shop first."))

		self._validate_adjustment_method()

		products = frappe.get_all(
			"Product",
			fields=["name", "uom", "stock_quantity"],
			filters={"shop": self.shop, "enabled": 1, "track_stock": 1},
		)

		for prod in products:
			current_stock = prod.get("stock_quantity", 0)
			quantity = current_stock if self.adjustment_method == "Adjust Stock" else 0
			self.append(
				"prodcuts",
				{
					"product": prod["name"],
					"uom": prod.get("uom", ""),
					"current_stock": current_stock,
					"quantity": quantity,
					"adjusted_stock": self._calculate_adjusted_stock(current_stock, quantity),
				},
			)

		return [d.as_dict() for d in self.prodcuts]

	@frappe.whitelist()
	def apply_adjustments(self):
		if not self.shop:
			frappe.throw(_("Please select a shop first."))

		self._validate_adjustment_method()

		if not self.prodcuts:
			frappe.throw(_("Please fetch products and enter the adjusted stock quantities first."))

		self._validate_products()

		updates = []
		for item in self.prodcuts:
			if not item.product:
				continue

			product = frappe.db.get_value(
				"Product",
				item.product,
				["item_name", "shop", "track_stock", "stock_quantity"],
				as_dict=True,
			)
			if not product or product.shop != self.shop or not product.track_stock:
				continue

			current_stock = product.stock_quantity or 0
			new_stock = self._calculate_adjusted_stock(current_stock, item.quantity)
			frappe.db.set_value("Product", item.product, "stock_quantity", new_stock)
			item.current_stock = current_stock
			item.adjusted_stock = new_stock
			updates.append((product.item_name or item.product, current_stock, new_stock))

		self.flags.ignore_mandatory = True
		self.save()

		if updates:
			frappe.msgprint(
				"<br>".join(
					(
						_("Set {0} stock to {1}").format(
							frappe.bold(frappe.utils.escape_html(name)),
							frappe.format_value(new_stock, {"fieldtype": "Float", "precision": "2"}),
						)
						if self.adjustment_method == "Adjust Stock"
						else _("Updated {0}: {1} -> {2} ({3})").format(
							frappe.bold(frappe.utils.escape_html(name)),
							frappe.format_value(current_stock, {"fieldtype": "Float", "precision": "2"}),
							frappe.format_value(new_stock, {"fieldtype": "Float", "precision": "2"}),
							self.adjustment_method,
						)
					)
					for name, current_stock, new_stock in updates
				),
				title=_("Stock Adjustment Summary"),
			)

		return {"updated": len(updates)}
