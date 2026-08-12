import frappe
from frappe import _
from phonenumbers import NumberParseException, PhoneNumberFormat, format_number, is_valid_number, parse


no_cache = 1


def get_context(context):
	slug = (frappe.form_dict.get("slug") or "").strip().lower()
	website = frappe.db.get_value(
		"Tookio Website",
		{"website_slug": slug, "enabled": 1},
		[
			"name",
			"website_name",
			"website_slug",
			"shop",
			"headline",
			"description",
			"whatsapp_number",
			"show_address",
		],
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
			"address",
			"mobile_number",
			"email_address",
			"shop_logo",
			"country",
			"currency",
		],
		as_dict=True,
	)
	if not shop:
		raise frappe.DoesNotExistError(_("This shop is currently unavailable."))

	products = frappe.get_all(
		"Product",
		filters={"shop": shop.name, "enabled": 1},
		fields=[
			"name",
			"item_name",
			"selling_price",
			"stock_quantity",
			"track_stock",
			"uom",
			"photo",
			"item_group",
		],
		order_by="modified desc",
	)
	products = [product for product in products if product.selling_price is not None]

	group_names = {}
	group_ids = {product.item_group for product in products if product.item_group}
	if group_ids:
		group_names = {
			row.name: row.group_name
			for row in frappe.get_all(
				"Tookio Item Group",
				filters={"name": ["in", list(group_ids)], "shop": shop.name, "enabled": 1},
				fields=["name", "group_name"],
			)
		}
	for product in products:
		product.group_label = group_names.get(product.item_group, _("Other"))
		product.in_stock = not product.track_stock or product.stock_quantity > 0
		product.stock_label = f"{float(product.stock_quantity or 0):g}"

	context.no_cache = 1
	context.no_breadcrumbs = 1
	context.show_sidebar = False
	context.full_width = True
	context.body_class = "tookio-storefront-page"
	context.title = website.website_name or shop.shop_name
	context.website = website
	context.shop = shop
	context.products = products
	context.groups = sorted({product.group_label for product in products})
	context.whatsapp_number = _format_whatsapp_number(
		website.whatsapp_number or shop.mobile_number,
		shop.country,
	)
	return context


def _format_whatsapp_number(number, country):
	"""Return a wa.me-compatible international number when country data is available."""
	if not number:
		return ""
	country_code = frappe.db.get_value("Country", country, "code") if country else None
	try:
		parsed = parse(number, country_code.upper() if country_code else None)
		if is_valid_number(parsed):
			return format_number(parsed, PhoneNumberFormat.E164).lstrip("+")
	except NumberParseException:
		pass
	return "".join(character for character in number if character.isdigit())
