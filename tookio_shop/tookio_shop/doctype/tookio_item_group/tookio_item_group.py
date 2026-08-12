import frappe
from frappe import _
from frappe.model.document import Document


class TookioItemGroup(Document):
	def validate(self):
		_validate_owned_shop(self.shop, self.owner)
		if frappe.db.exists("Tookio Item Group", {"shop": self.shop, "item_group_name": self.item_group_name, "name": ("!=", self.name)}):
			frappe.throw(_("An item group with this name already exists in this shop."))


def _validate_owned_shop(shop, owner):
	shop_owner = frappe.db.get_value("Shop", shop, "owner")
	if not shop_owner:
		frappe.throw(_("Select a valid shop."))
	if owner != shop_owner and "System Manager" not in frappe.get_roles():
		frappe.throw(_("You can only use shops that you own."))
