import frappe
from frappe.utils import getdate, add_months, escape_html


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
    # First, try to get any subscription (Active or Expired)
    user_sub = frappe.db.get_value(
        "Tookio User Subscription",
        {"user": user},
        ["shop_limit", "products_limit", "sales_invoice_limit", "status", "subscription_end_date"],
        as_dict=True
    )
    
    if user_sub:
        # Check if expired and auto-downgrade to free plan
        if user_sub.subscription_end_date:
            try:
                from frappe.utils import getdate, today
                if getdate(user_sub.subscription_end_date) < getdate(today()) and user_sub.status != "Expired":
                    # Auto-downgrade to free plan
                    frappe.db.set_value("Tookio User Subscription", {"user": user}, {
                        "status": "Expired",
                        "current_subscription": "Free Plan",
                        "shop_limit": 1,
                        "products_limit": 50,
                        "sales_invoice_limit": 200,
                        "subscription_end_date": None
                    })
                    frappe.db.commit()
                    # Return free plan limits
                    return {
                        "custom_shop_limit": 1,
                        "custom_item_limits": 50,
                        "sales_invoice_limit": 200
                    }
            except Exception as e:
                frappe.logger().error(f"Error checking subscription expiry in utils: {str(e)}")
        
        return {
            "custom_shop_limit": user_sub.shop_limit or 1,
            "custom_item_limits": user_sub.products_limit or 50,
            "sales_invoice_limit": user_sub.sales_invoice_limit or 200
        }
    
    # No subscription found, return free plan defaults
    return {
        "custom_shop_limit": 1,
        "custom_item_limits": 50,
        "sales_invoice_limit": 200
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


def ensure_active_subscription(user=None):
    """Enforce active subscription status before allowing any transactional insert."""
    current_user = user or frappe.session.user
    status = frappe.db.get_value("Tookio User Subscription", {"user": current_user}, "status")

    if status and status.lower() != "active":
        frappe.throw("Your plan is expired kindly renew or switch to free plan")
    return True


def check_item_limit(doc, method):
    """Check if user has exceeded their item limit"""
    user = frappe.session.user

    ensure_active_subscription(user)
    
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

    ensure_active_subscription(user)
    
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
        product = frappe.db.get_value(
            "Product",
            item.product,
            ["item_name", "stock_quantity", "track_stock"],
            as_dict=True,
        )

        if not product or not product.track_stock:
            continue

        stock = product.stock_quantity or 0
        if item.quantity > stock:
            product_name = product.item_name or item.product
            frappe.throw(
                f"There is not enough stock for <strong>{escape_html(product_name)}</strong>. "
                f"Available stock: {stock}. Requested quantity: {item.quantity}."
            )

def check_sales_invoice_limit(doc, method):
    """Check if user has exceeded their sales invoice limit"""
    user = frappe.session.user

    ensure_active_subscription(user)
    
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


@frappe.whitelist()
@frappe.whitelist()
def delete_user_account(user=None, password=None):
    """
    Delete/disable a user account for GDPR compliance
    """
    import frappe
    from frappe import _
    from frappe.utils import now

    # Get current user
    current_user = frappe.session.user

    # If no user specified, use current user
    if not user:
        user = current_user

    # Allow deletion of any user account as long as correct password is provided
    # (no restrictions - password verification provides security)

    # Verify password is provided
    if not password:
        frappe.throw(_('Password is required to delete account'))

    # Verify password
    try:
        # Get user document to check password
        user_doc = frappe.get_doc('User', user)
        
        # Check if password is correct
        if not frappe.check_password(user, password):
            frappe.throw(_('Incorrect password'))
            
    except frappe.AuthenticationError:
        frappe.throw(_('Incorrect password'))
    except Exception as e:
        frappe.log_error(f'Password verification failed for user {user}: {str(e)}')
        frappe.throw(_('Password verification failed'))

    try:
        # Disable the user account instead of deleting (for audit trail)
        user_doc.enabled = 0
        user_doc.save(ignore_permissions=True)

        # Log the action
        frappe.logger().info(f'User account disabled: {user} by {current_user} at {now()}')

        # If user is deleting their own account, clear session to log them out
        if user == current_user:
            frappe.local.session_obj = None
            frappe.local.session = None
            frappe.session.user = 'Guest'

        # Commit the changes
        frappe.db.commit()

        return {'success': True, 'message': _('Account disabled successfully')}

    except Exception as e:
        frappe.log_error(f'Error deleting user account {user}: {str(e)}')
        frappe.db.rollback()
        return {'success': False, 'error': str(e)}

def update_website_context(context):
    """Override context for specific pages"""
    if frappe.local.request and frappe.local.request.path.startswith('/login'):
        # Force show header and footer on login page
        context.no_header = False
        context.show_language_picker = True
        context.show_footer_on_login = 1
