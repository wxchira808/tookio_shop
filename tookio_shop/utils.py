import frappe




def setup_new_user(doc, method):
    # Add at start of function
    frappe.log_error(
        f"Debug - Current Module Profile: {doc.module_profile}\n"
        f"Current Roles: {doc.roles}\n"
        f"Boot Info: {frappe.session.boot.allowed_modules if frappe.session.boot else 'No Boot'}",
        "Module Debug"
    )
    """Setup Tookio Seller role and module access for new users - NO TIERING SYSTEM"""
    try:
        # 1. Set role profile and module profile first
        frappe.db.set_value('User', doc.name, {
            'module_profile': 'Tookio Seller',
            'role_profile_name': 'Tookio Seller',
            'home_settings': '{"desktop_icons": ["Tookio Seller"]}'
        })

        # 2. NO CUSTOMER CREATION - REMOVED FOR UNLIMITED FREE APP
        # Removed all customer creation and subscription logic

        # 3. Assign ONLY Tookio Seller role using direct SQL to bypass permissions
        for role in ["Tookio Seller"]:  # REMOVED "Customer" role
            if not frappe.db.exists("Has Role", {"parent": doc.name, "role": role}):
                frappe.db.sql("""
                    INSERT INTO `tabHas Role` (name, creation, modified, modified_by, owner, parent, parentfield,
                    parenttype, idx, role) VALUES (UUID(), NOW(), NOW(), 'Administrator', 'Administrator', %s, 'roles', 'User', 1, %s)
                """, (doc.name, role))

        # 4. Set module access - first remove all modules
        frappe.db.sql("DELETE FROM `tabBlock Module` WHERE parent = %s", (doc.name,))

        # Get all modules except Tookio Seller to block them
        modules = frappe.db.sql("""
            SELECT name FROM `tabModule Def`
            WHERE name != 'Tookio Seller'
            AND name NOT IN ('Core', 'Website')
        """, as_dict=1)

        # Block all modules except Tookio Seller
        for module in modules:
            frappe.db.sql("""
                INSERT INTO `tabBlock Module` (name, creation, modified, modified_by, owner, parent,
                parentfield, parenttype, module)
                VALUES (UUID(), NOW(), NOW(), 'Administrator', 'Administrator', %s, 'block_modules', 'User', %s)
            """, (doc.name, module.name))

        frappe.db.commit()
        frappe.log_error(f"Successfully set up new user {doc.name} with Tookio Shop module only - NO TIERING", "Setup User Success")
    except Exception as e:
        frappe.log_error(f"Error setting up user {doc.name}: {str(e)}", "Setup User Error")
    

def get_user_plan_limits(user):
    """UNLIMITED FREE APP - No limits for any user"""
    return {"custom_item_limits": 999999, "custom_shop_limit": 999999}

def check_item_limit(doc, method):
    """UNLIMITED FREE APP - No item limits"""
    pass  # No limits in free app

def check_shop_limit(doc, method):
    """UNLIMITED FREE APP - No shop limits"""
    pass  # No limits in free app

def prevent_negative_stock(doc, method):
    for item in doc.items:
        # Always fetch latest stock from DB, not from item_stock field
        stock = frappe.db.get_value("Product", item.product, "stock_quantity") or 0
        if item.quantity > stock:
            frappe.throw(f"Not enough stock for {item.product}. Available: {stock}, Requested: {item.quantity}")

def check_and_handle_expired_subscriptions():
    """UNLIMITED FREE APP - No subscriptions to expire"""
    pass  # No subscriptions in free app

def get_user_subscription_status(user=None):
    """UNLIMITED FREE APP - Always return unlimited status"""
    return {"custom_item_limits": 999999, "custom_shop_limit": 999999}


def get_enabled_products_for_user(shop=None):
	"""Get only enabled products for a specific shop or all enabled products"""
	filters = {'enabled': 1}
	if shop:
		filters['shop'] = shop
	
	return frappe.get_list('Product', 
		filters=filters,
		fields=['name', 'item_name', 'selling_price', 'stock_quantity', 'shop', 'enabled'],
		order_by='item_name asc'
	)


def validate_product_is_enabled(product_name):
	"""Check if a product is enabled, raise error if disabled"""
	is_enabled = frappe.db.get_value('Product', product_name, 'enabled')
	if not is_enabled:
		frappe.throw(f"Product '{product_name}' is disabled and cannot be used in transactions.")
	return True






