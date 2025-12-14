import frappe
from frappe.utils import getdate, add_months


def setup_new_user(doc, method):
    """Setup Tookio Seller role and create free subscription for new users"""
    try:
        # 1. Set role profile and module profile first
        frappe.db.set_value('User', doc.name, {
            'module_profile': 'Tookio Seller',
            'role_profile_name': 'Tookio Seller',
            'home_settings': '{"desktop_icons": ["Tookio Seller"]}'
        })

        # 2. Assign Tookio Seller role using direct SQL to bypass permissions
        for role in ["Tookio Seller"]:
            if not frappe.db.exists("Has Role", {"parent": doc.name, "role": role}):
                frappe.db.sql("""
                    INSERT INTO `tabHas Role` (name, creation, modified, modified_by, owner, parent, parentfield,
                    parenttype, idx, role) VALUES (UUID(), NOW(), NOW(), 'Administrator', 'Administrator', %s, 'roles', 'User', 1, %s)
                """, (doc.name, role))

        # 3. Set module access - block all modules except Tookio Seller
        frappe.db.sql("DELETE FROM `tabBlock Module` WHERE parent = %s", (doc.name,))

        modules = frappe.db.sql("""
            SELECT name FROM `tabModule Def`
            WHERE name != 'Tookio Seller'
            AND name NOT IN ('Core', 'Website')
        """, as_dict=1)

        for module in modules:
            frappe.db.sql("""
                INSERT INTO `tabBlock Module` (name, creation, modified, modified_by, owner, parent,
                parentfield, parenttype, module)
                VALUES (UUID(), NOW(), NOW(), 'Administrator', 'Administrator', %s, 'block_modules', 'User', %s)
            """, (doc.name, module.name))

        # 4. Create Free Plan subscription for new user
        create_free_subscription_for_user(doc.name)

        frappe.db.commit()
        frappe.logger().info(f"Successfully set up new user {doc.name} with Free Plan subscription")
    except Exception as e:
        frappe.log_error(f"Error setting up user {doc.name}: {str(e)}", "Setup User Error")


def create_free_subscription_for_user(user):
    """Create a free subscription for the user"""
    try:
        # Check if user already has a subscription
        existing_sub = frappe.db.exists("Tookio User Subscription", {"user": user})
        if existing_sub:
            frappe.logger().info(f"User {user} already has a subscription")
            return

        # Get the Free Plan
        free_plan = frappe.db.get_value("Tookio Subscription", {"subscription_name": "Free Plan"}, "name")
        
        if not free_plan:
            frappe.log_error("Free Plan not found", "Auto Subscription Creation")
            return

        # Set the user as the session user temporarily to make them the owner
        frappe.set_user(user)
        
        # Create user subscription
        user_sub = frappe.new_doc("Tookio User Subscription")
        user_sub.user = user
        user_sub.current_subscription = free_plan
        user_sub.subscription_start_date = getdate()
        user_sub.subscription_end_date = add_months(getdate(), 600)  # Free plan for 50 years
        user_sub.status = "Active"
        user_sub.insert(ignore_permissions=True)
        
        # Reset to Administrator
        frappe.set_user("Administrator")
        
        frappe.db.commit()
        frappe.logger().info(f"Created free subscription for user {user}")
    except Exception as e:
        frappe.set_user("Administrator")  # Reset even on error
        frappe.log_error(f"Error creating free subscription for user {user}: {str(e)}", "Auto Subscription Creation Failed")
    

def get_user_plan_limits(user):
    """Get user's subscription plan limits"""
    user_sub = frappe.db.get_value(
        "Tookio User Subscription",
        {"user": user, "status": "Active"},
        ["shop_limit", "products_limit", "sales_invoice_limit"],
        as_dict=True
    )
    
    if user_sub:
        return {
            "custom_shop_limit": user_sub.shop_limit,
            "custom_item_limits": user_sub.products_limit,
            "sales_invoice_limit": user_sub.sales_invoice_limit
        }


def check_subscription_expired(user):
    """Check if user's subscription has expired"""
    user_sub = frappe.db.get_value(
        "Tookio User Subscription",
        {"user": user},
        ["subscription_end_date", "status"],
        as_dict=True
    )
    
    if user_sub and user_sub.subscription_end_date:
        if getdate(user_sub.subscription_end_date) < getdate():
            # Subscription expired, deactivate it
            if user_sub.status == "Active":
                frappe.db.set_value("Tookio User Subscription", {"user": user}, "status", "Expired")
                frappe.db.commit()
            return True
    return False
    else:
        # Default to free plan limits if no subscription found
        return {
            "custom_shop_limit": 1,
            "custom_item_limits": 50,
            "sales_invoice_limit": 200
        }

def check_item_limit(doc, method):
    """Check if user has exceeded their item limit"""
    user = frappe.session.user
    
    # Check if subscription expired
    if check_subscription_expired(user):
        frappe.throw("Your subscription has expired. Please renew to continue using Tookio Shop.")
    
    limits = get_user_plan_limits(user)
    
    # Count existing products for this user
    product_count = frappe.db.count("Product", {"owner": user})
    
    if product_count >= limits["custom_item_limits"]:
        frappe.throw(
            f"You have reached your product limit of {limits['custom_item_limits']}. "
            f"Please upgrade your subscription to add more products."
        )

def check_shop_limit(doc, method):
    """Check if user has exceeded their shop limit"""
    user = frappe.session.user
    
    # Check if subscription expired
    if check_subscription_expired(user):
        frappe.throw("Your subscription has expired. Please renew to continue using Tookio Shop.")
    
    limits = get_user_plan_limits(user)
    
    # Count existing shops for this user
    shop_count = frappe.db.count("Shop", {"owner": user})
    
    if shop_count >= limits["custom_shop_limit"]:
        frappe.throw(
            f"You have reached your shop limit of {limits['custom_shop_limit']}. "
            f"Please upgrade your subscription to add more shops."
        )

def prevent_negative_stock(doc, method):
    for item in doc.items:
        # Always fetch latest stock from DB, not from item_stock field
        stock = frappe.db.get_value("Product", item.product, "stock_quantity") or 0
        if item.quantity > stock:
            frappe.throw(f"Not enough stock for {item.product}. Available: {stock}, Requested: {item.quantity}")

def check_sales_invoice_limit(doc, method):
    """Check if user has exceeded their sales invoice limit"""
    user = frappe.session.user
    
    # Check if subscription expired
    if check_subscription_expired(user):
        frappe.throw("Your subscription has expired. Please renew to continue using Tookio Shop.")
    
    limits = get_user_plan_limits(user)
    
    # 0 means unlimited
    if limits["sales_invoice_limit"] == 0:
        return
    
    # Count existing sales invoices for this user
    invoice_count = frappe.db.count("Sale Invoice", {"owner": user})
    
    if invoice_count >= limits["sales_invoice_limit"]:
        frappe.throw(
            f"You have reached your sales invoice limit of {limits['sales_invoice_limit']}. "
            f"Please upgrade your subscription to create more invoices."
        )

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






