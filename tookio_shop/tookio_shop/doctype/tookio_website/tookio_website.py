import re

import frappe
from frappe import _
from frappe.model.document import Document

from tookio_shop.utils import check_website_limit, get_user_plan_limits


class TookioWebsite(Document):
	def before_insert(self):
		_validate_owned_shop(self.shop, self.owner)
		check_website_limit(self, None)

	def validate(self):
		_validate_owned_shop(self.shop, self.owner)
		self.website_slug = _normalise_slug(self.website_slug or self.website_name)
		if not self.website_slug:
			frappe.throw(_("Enter a website name that can be used in a URL."))
		if self.enabled and not get_user_plan_limits(self.owner)["website_enabled"]:
			frappe.throw(_("Your current plan does not include a Tookio Website."))


def _validate_owned_shop(shop, owner):
	shop_owner = frappe.db.get_value("Shop", shop, "owner")
	if not shop_owner:
		frappe.throw(_("Select a valid shop."))
	if owner != shop_owner and "System Manager" not in frappe.get_roles():
		frappe.throw(_("You can only create a website for a shop that you own."))


def _normalise_slug(value):
	value = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
	if value in {"www", "app", "api", "admin", "login", "assets", "mail"}:
		frappe.throw(_("This website slug is reserved."))
	return value
