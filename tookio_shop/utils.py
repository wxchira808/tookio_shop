import frappe
from frappe.utils import getdate, add_months, escape_html, today


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

        # Create user subscription
        user_sub = frappe.new_doc("Tookio User Subscription")
        user_sub.owner = user
        user_sub.user = user
        user_sub.current_subscription = free_plan
        user_sub.subscription_start_date = getdate()
        user_sub.subscription_end_date = None
        user_sub.status = "Active"
        user_sub.insert(ignore_permissions=True)
        
        frappe.db.commit()
        frappe.logger().info(f"Created free subscription for user {user}")
    except Exception as e:
        frappe.log_error(f"Error creating free subscription for user {user}: {str(e)}", "Auto Subscription Creation Failed")
    

PLAN_LIMIT_FIELDS = [
    "shop_limit",
    "products_limit",
    "sales_invoice_limit",
    "website_enabled",
    "website_limit",
]


def get_free_plan_name():
    free_plan = frappe.db.get_value("Tookio Subscription", {"subscription_name": "Free Plan", "enabled": 1}, "name")
    if not free_plan:
        frappe.throw("Configure an enabled Free Plan before creating users or checking limits.")
    return free_plan


def get_plan_limits(plan_name):
    plan = frappe.db.get_value("Tookio Subscription", plan_name, PLAN_LIMIT_FIELDS, as_dict=True)
    if not plan:
        frappe.throw("The selected subscription plan no longer exists.")
    return plan


def sync_subscription_limits(subscription_name, plan_name=None, status=None, end_date=None):
    subscription = frappe.get_doc("Tookio User Subscription", subscription_name)
    plan_name = plan_name or subscription.current_subscription
    limits = get_plan_limits(plan_name)
    subscription.current_subscription = plan_name
    subscription.shop_limit = limits.shop_limit
    subscription.products_limit = limits.products_limit
    subscription.sales_invoice_limit = limits.sales_invoice_limit
    subscription.website_enabled = limits.website_enabled
    subscription.website_limit = limits.website_limit
    if status is not None:
        subscription.status = status
    if end_date is not None:
        subscription.subscription_end_date = end_date
    subscription.save(ignore_permissions=True)
    return limits


def _downgrade_expired_subscription(subscription):
    if not subscription.subscription_end_date or getdate(subscription.subscription_end_date) >= getdate(today()):
        return False
    free_plan = get_free_plan_name()
    subscription.current_subscription = free_plan
    subscription.subscription_start_date = getdate(today())
    subscription.subscription_end_date = None
    subscription.status = "Active"
    limits = get_plan_limits(free_plan)
    subscription.shop_limit = limits.shop_limit
    subscription.products_limit = limits.products_limit
    subscription.sales_invoice_limit = limits.sales_invoice_limit
    subscription.website_enabled = limits.website_enabled
    subscription.website_limit = limits.website_limit
    subscription.save(ignore_permissions=True)
    return True


def get_user_plan_limits(user):
    """Return limits from the user's current plan. A value of 0 means unlimited."""
    subscription_name = frappe.db.exists("Tookio User Subscription", {"user": user})
    if not subscription_name:
        create_free_subscription_for_user(user)
        subscription_name = frappe.db.exists("Tookio User Subscription", {"user": user})
    if not subscription_name:
        frappe.throw("No subscription record could be created for this user.")

    subscription = frappe.get_doc("Tookio User Subscription", subscription_name)
    _downgrade_expired_subscription(subscription)
    subscription.reload()
    limits = get_plan_limits(subscription.current_subscription)
    return {
        "custom_shop_limit": limits.shop_limit,
        "custom_item_limits": limits.products_limit,
        "sales_invoice_limit": limits.sales_invoice_limit,
        "website_enabled": bool(limits.website_enabled),
        "website_limit": limits.website_limit,
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
            subscription_name = frappe.db.exists("Tookio User Subscription", {"user": user})
            if subscription_name:
                _downgrade_expired_subscription(frappe.get_doc("Tookio User Subscription", subscription_name))
            return True
    return False


def ensure_active_subscription(user=None):
    """Enforce active subscription status before allowing any transactional insert."""
    current_user = user or frappe.session.user
    get_user_plan_limits(current_user)
    status = frappe.db.get_value("Tookio User Subscription", {"user": current_user}, "status")

    if status and status.lower() != "active":
        frappe.throw("Your plan is expired kindly renew or switch to free plan")
    return True


def check_item_limit(doc, method):
    """Check if user has exceeded their item limit"""
    user = doc.owner or frappe.session.user

    ensure_active_subscription(user)
    
    limits = get_user_plan_limits(user)
    
    # Count existing products for this user
    product_count = frappe.db.count("Product", {"owner": user})
    
    # 0 means unlimited.
    if limits["custom_item_limits"] != 0 and product_count >= limits["custom_item_limits"]:
        frappe.throw(
            f"You have reached your product limit of {limits['custom_item_limits']}. "
            f"Please upgrade your subscription to add more products."
        )

def check_shop_limit(doc, method):
    """Check if user has exceeded their shop limit"""
    user = doc.owner or frappe.session.user

    ensure_active_subscription(user)
    
    limits = get_user_plan_limits(user)
    
    # Count existing shops for this user
    shop_count = frappe.db.count("Shop", {"owner": user})
    
    # 0 means unlimited.
    if limits["custom_shop_limit"] != 0 and shop_count >= limits["custom_shop_limit"]:
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
    user = doc.owner or frappe.session.user

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

def check_website_limit(doc, method):
    """Enforce website access. 0 means unlimited only after Website Access is enabled."""
    user = doc.owner or frappe.session.user
    ensure_active_subscription(user)
    limits = get_user_plan_limits(user)
    if not limits["website_enabled"]:
        frappe.throw("Your current plan does not include a Tookio Website.")
    if limits["website_limit"] == 0:
        return
    website_count = frappe.db.count("Tookio Website", {"owner": user})
    if website_count >= limits["website_limit"]:
        frappe.throw(f"You have reached your website limit of {limits['website_limit']}. Please upgrade your subscription to add more websites.")


def check_and_handle_expired_subscriptions():
    """Downgrade expired paid subscriptions to the data-configured Free Plan."""
    subscriptions = frappe.get_all(
        "Tookio User Subscription",
        filters={"status": "Active", "subscription_end_date": ("is", "set")},
        pluck="name",
    )
    for subscription_name in subscriptions:
        _downgrade_expired_subscription(frappe.get_doc("Tookio User Subscription", subscription_name))

def get_user_subscription_status(user=None):
    return get_user_plan_limits(user or frappe.session.user)


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
