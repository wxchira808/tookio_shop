import frappe


PLAN_VALUES = {
	"Free Plan": {
		"subscription_name": "Free Plan",
		"description": "Perfect for getting started with basic shop management.",
		"price": 0,
		"currency": "KES",
		"website_enabled": 0,
		"website_limit": 0,
		"enabled": 1,
	},
	"Starter Plan": {
		"subscription_name": "Starter Plan",
		"description": "For one growing shop with stock, sales, expenses, and unlimited invoices.",
		"price": 450,
		"currency": "KES",
		"website_enabled": 0,
		"website_limit": 0,
		"enabled": 1,
	},
	"Pro Plan": {
		"subscription_name": "Pro Plan",
		"description": "For sellers with unlimited shops who need one public Tookio Website.",
		"price": 1000,
		"currency": "KES",
		"shop_limit": 0,
		"products_limit": 0,
		"sales_invoice_limit": 0,
		"website_enabled": 1,
		"website_limit": 1,
		"enabled": 1,
	},
	"Premium Plan": {
		"subscription_name": "Premium Plan",
		"description": "For sellers managing multiple shops and up to five separate Tookio Websites.",
		"price": 2500,
		"currency": "KES",
		"shop_limit": 0,
		"products_limit": 0,
		"sales_invoice_limit": 0,
		"website_enabled": 1,
		"website_limit": 5,
		"enabled": 1,
	},
}


def execute():
	# The old KES 1,160 Premium record was the public-facing Pro tier. Rename it
	# before adding the new Premium tier so existing subscribers keep its access.
	if frappe.db.exists("Tookio Subscription", "Premium Plan") and not frappe.db.exists("Tookio Subscription", "Pro Plan"):
		frappe.rename_doc("Tookio Subscription", "Premium Plan", "Pro Plan", force=True)

	for name, values in PLAN_VALUES.items():
		existing_name = frappe.db.get_value("Tookio Subscription", {"subscription_name": values["subscription_name"]}, "name")
		if existing_name and existing_name != name:
			frappe.rename_doc("Tookio Subscription", existing_name, name, force=True)
		if frappe.db.exists("Tookio Subscription", name):
			frappe.db.set_value("Tookio Subscription", name, values, update_modified=False)
		else:
			plan = frappe.get_doc({"doctype": "Tookio Subscription", **values})
			plan.insert(ignore_permissions=True)
			frappe.rename_doc("Tookio Subscription", plan.name, name, force=True)

	for subscription_name in frappe.get_all("Tookio User Subscription", pluck="name"):
		subscription = frappe.get_doc("Tookio User Subscription", subscription_name)
		if not frappe.db.exists("Tookio Subscription", subscription.current_subscription):
			subscription.current_subscription = "Free Plan"
		plan = frappe.get_doc("Tookio Subscription", subscription.current_subscription)
		frappe.db.set_value(
			"Tookio User Subscription",
			subscription_name,
			{
				"shop_limit": plan.shop_limit,
				"products_limit": plan.products_limit,
				"sales_invoice_limit": plan.sales_invoice_limit,
				"website_enabled": plan.website_enabled,
				"website_limit": plan.website_limit,
			},
			update_modified=False,
		)
