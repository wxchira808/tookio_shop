import frappe
from frappe import _
from frappe.utils.html_utils import sanitize_html

from tookio_shop.www.store.index import _format_whatsapp_number


no_cache = 1


def get_context(context):
	slug = (frappe.form_dict.get("slug") or "").strip().lower()
	product_name = frappe.form_dict.get("product")

	website = frappe.db.get_value(
		"Tookio Website",
		{"website_slug": slug, "enabled": 1},
		["website_name", "website_slug", "shop", "whatsapp_number", "show_address"],
		as_dict=True,
	)
	if not website:
		raise frappe.DoesNotExistError(_("This shop website is unavailable."))

	shop = frappe.db.get_value(
		"Shop",
		{"name": website.shop, "enabled": 1},
		[
			"name",
			"shop_name",
			"location",
			"mobile_number",
			"shop_logo",
			"country",
			"currency",
		],
		as_dict=True,
	)
	if not shop:
		raise frappe.DoesNotExistError(_("This shop is currently unavailable."))

	product = frappe.db.get_value(
		"Product",
		{"name": product_name, "shop": shop.name, "enabled": 1},
		[
			"name",
			"item_name",
			"description",
			"selling_price",
			"stock_quantity",
			"track_stock",
			"photo",
			"item_group",
			"uom",
		],
		as_dict=True,
	)
	if not product or product.selling_price is None:
		raise frappe.DoesNotExistError(_("This product is unavailable."))

	product.group_label = _("Other")
	if product.item_group:
		product.group_label = frappe.db.get_value(
			"Tookio Item Group",
			{"name": product.item_group, "shop": shop.name, "enabled": 1},
			"group_name",
		) or _("Other")
	product.in_stock = not product.track_stock or product.stock_quantity > 0
	product.stock_label = f"{float(product.stock_quantity or 0):g}"

	context.no_cache = 1
	context.no_breadcrumbs = 1
	context.show_sidebar = False
	context.full_width = True
	context.body_class = "tookio-storefront-page"
	context.title = f"{product.item_name} — {shop.shop_name}"
	context.website = website
	context.shop = shop
	context.product = product
	context.product_description = sanitize_html(product.description or "")
	context.whatsapp_number = _format_whatsapp_number(
		website.whatsapp_number or shop.mobile_number,
		shop.country,
	)
	return context
