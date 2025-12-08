import frappe




def setup_new_user(doc, method):
    # Add at start of function
    frappe.log_error(
        f"Debug - Current Module Profile: {doc.module_profile}\n"
        f"Current Roles: {doc.roles}\n"
        f"Boot Info: {frappe.session.boot.allowed_modules if frappe.session.boot else 'No Boot'}", 
        "Module Debug"
    )
    """Setup Tookio Seller role and module access for new users"""
    # 1. Set role profile and module profile first
    frappe.db.set_value('User', doc.name, {
        'module_profile': 'Tookio Seller',
        'role_profile_name': 'Tookio Seller',
    })

    # 2. Create customer profile
    customer_name = None
    portal_user = frappe.db.get_value(
        "Portal User", {"user": doc.name}, "parent"
    )
    if portal_user:
        customer_name = portal_user
    else:
        # No customer with this user, create new Customer
        customer = frappe.new_doc("Customer")
        customer.customer_name = doc.full_name or doc.name
        customer.customer_group = "Tookio Seller"  # adjust as per your setup
        customer.territory = "All Territories"
        customer.append("portal_users", {"user": doc.name})
        customer.insert(ignore_permissions=True)
        customer_name = customer.name

    try:
        # 1. Set role profile and module profile first
        frappe.db.set_value('User', doc.name, {
            'module_profile': 'Tookio Seller',
            'role_profile_name': 'Tookio Seller',
            'home_settings': '{"desktop_icons": ["Tookio Seller"]}'
        })

        # 2. Create customer profile
        customer_name = None
        portal_user = frappe.db.get_value(
            "Portal User", {"user": doc.name}, "parent"
        )
        if portal_user:
            customer_name = portal_user
        else:
            customer = frappe.new_doc("Customer")
            customer.customer_name = doc.full_name or doc.name
            customer.customer_group = "Tookio Seller"
            customer.territory = "All Territories"
            customer.append("portal_users", {"user": doc.name})
            customer.insert(ignore_permissions=True)
            customer_name = customer.name

        # 3. Assign Free Plan and create subscription
        plan_name = "Free Plan"
        if frappe.db.exists("Subscription Plan", plan_name):
            customer = frappe.get_doc("Customer", customer_name, ignore_permissions=True)
            customer.db_set("custom_tookio_subscription_plan", plan_name)
            
            # Create a proper subscription for the free plan
            if not frappe.db.exists("Subscription", {"party": customer_name}):
                # Get plan billing details
                plan_billing = frappe.db.get_value(
                    "Subscription Plan", 
                    plan_name, 
                    ["billing_interval", "billing_interval_count"], 
                    as_dict=True
                )
                
                # Calculate proper end date for free plan
                start_date = frappe.utils.today()
                if plan_billing and plan_billing.billing_interval == "Year":
                    end_date = frappe.utils.add_years(start_date, plan_billing.billing_interval_count or 1)
                else:
                    # Default free plan to 1 year
                    end_date = frappe.utils.add_years(start_date, 1)
                
                subscription = frappe.new_doc("Subscription")
                subscription.party_type = "Customer"
                subscription.party = customer_name
                subscription.status = "Active"
                subscription.start_date = start_date
                subscription.end_date = end_date
                subscription.current_invoice_start = start_date
                subscription.current_invoice_end = end_date
                subscription.append("plans", {
                    "plan": plan_name,
                    "qty": 1
                })
                subscription.insert(ignore_permissions=True)

        # 4. Assign the roles using direct SQL to bypass permissions
        for role in ["Tookio Seller", "Customer"]:
            if not frappe.db.exists("Has Role", {"parent": doc.name, "role": role}):
                frappe.db.sql("""
                    INSERT INTO `tabHas Role` (name, creation, modified, modified_by, owner, parent, parentfield, 
                    parenttype, idx, role) VALUES (UUID(), NOW(), NOW(), 'Administrator', 'Administrator', %s, 'roles', 'User', 1, %s)
                """, (doc.name, role))

        # 5. Set module access - first remove all modules
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
        frappe.log_error(f"Successfully set up new user {doc.name} with Tookio Shop module only", "Setup User Success")
    except Exception as e:
        frappe.log_error(f"Error setting up user {doc.name}: {str(e)}", "Setup User Error")
    

def get_user_plan_limits(user):
    # Find Customer via Portal User child table
    customer_name = frappe.db.get_value("Portal User", {"user": user}, "parent")
    if customer_name:
        # Get the linked subscription plan from Customer
        plan_name = frappe.db.get_value("Customer", customer_name, "custom_tookio_subscription_plan")
        if plan_name:
            limits = frappe.db.get_value(
                "Subscription Plan", plan_name,
                ["custom_item_limits", "custom_shop_limit"],
                as_dict=True
            )
            if limits:
                return limits
    return {"custom_item_limits": 25, "custom_shop_limit": 1}

def check_item_limit(doc, method):
    limits = get_user_subscription_status(frappe.session.user)
    count = frappe.db.count("Product", {"owner": frappe.session.user})
    if count >= limits["custom_item_limits"]:
        frappe.throw("Item limit reached. Please upgrade your plan.")

def check_shop_limit(doc, method):
    limits = get_user_subscription_status(frappe.session.user)
    count = frappe.db.count("Shop", {"owner": frappe.session.user})
    if count >= limits["custom_shop_limit"]:
        frappe.throw("Shop limit reached. Please upgrade your plan.")

def prevent_negative_stock(doc, method):
    for item in doc.items:
        # Always fetch latest stock from DB, not from item_stock field
        stock = frappe.db.get_value("Product", item.product, "stock_quantity") or 0
        if item.quantity > stock:
            frappe.throw(f"Not enough stock for {item.product}. Available: {stock}, Requested: {item.quantity}")

def check_and_handle_expired_subscriptions():
    """
    Function to check for expired subscriptions and downgrade them to Free Plan.
    This should be called via a scheduled job (cron).
    """
    try:
        # Find all active subscriptions that have expired
        expired_subscriptions = frappe.db.sql("""
            SELECT name, party, end_date 
            FROM `tabSubscription` 
            WHERE status = 'Active' 
            AND end_date < %s
        """, (frappe.utils.today(),), as_dict=True)
        
        for sub in expired_subscriptions:
            try:
                # Get the customer
                customer = frappe.get_doc("Customer", sub.party)
                
                # Check if Free Plan exists
                if frappe.db.exists("Subscription Plan", "Free Plan"):
                    # Update customer to Free Plan
                    customer.custom_tookio_subscription_plan = "Free Plan"
                    customer.save(ignore_permissions=True)
                    
                    # Update subscription to Free Plan and extend for 1 year
                    subscription = frappe.get_doc("Subscription", sub.name)
                    subscription.plans = []  # Clear existing plans
                    subscription.append("plans", {
                        "plan": "Free Plan",
                        "qty": 1
                    })
                    
                    # Calculate new end date
                    today = frappe.utils.today()
                    new_end_date = frappe.utils.add_years(today, 1)
                    
                    # Use db_set to avoid validation issues
                    try:
                        subscription.save(ignore_permissions=True)
                        
                        # Update dates using db_set to bypass validations
                        subscription.db_set("end_date", new_end_date)
                        subscription.db_set("current_invoice_start", today)
                        subscription.db_set("current_invoice_end", new_end_date)
                        
                    except Exception as e:
                        frappe.logger().error(f"Error updating expired subscription {sub.name}: {str(e)}")
                        # If save fails, try using db_set for everything
                        subscription.db_set("status", "Active")
                        subscription.db_set("end_date", new_end_date)
                        subscription.db_set("current_invoice_start", today)
                        subscription.db_set("current_invoice_end", new_end_date)
                    
                    frappe.logger().info(f"Subscription {sub.name} for customer {sub.party} downgraded to Free Plan due to expiry on {sub.end_date}")
                else:
                    # If no Free Plan, mark subscription as expired
                    subscription = frappe.get_doc("Subscription", sub.name)
                    subscription.status = "Expired"
                    subscription.save(ignore_permissions=True)
                    
                    frappe.logger().warning(f"Subscription {sub.name} marked as expired - no Free Plan available")
                    
            except Exception as e:
                frappe.log_error(f"Error handling expired subscription {sub.name}: {str(e)}", "Subscription Expiry Error")
                
    except Exception as e:
        frappe.log_error(f"Error in check_and_handle_expired_subscriptions: {str(e)}", "Subscription Expiry Check Error")

def get_user_subscription_status(user=None):
    """
    Get the current subscription status for a user, handling expired subscriptions
    """
    if not user:
        user = frappe.session.user
        
    # First check for expired subscriptions and handle them
    customer_name = frappe.db.get_value("Portal User", {"user": user}, "parent")
    if customer_name:
        subscription = frappe.db.get_value(
            "Subscription",
            {"party": customer_name},
            ["name", "status", "end_date"],
            as_dict=True
        )
        
        if subscription and subscription.status == "Active":
            # Check if subscription has expired
            if subscription.end_date and subscription.end_date < frappe.utils.getdate():
                # Handle the expired subscription
                try:
                    check_and_handle_expired_subscriptions()
                    # Refetch after handling expiry
                    return get_user_plan_limits(user)
                except Exception as e:
                    frappe.log_error(f"Error handling expired subscription for user {user}: {str(e)}", "Subscription Status Error")
    
    return get_user_plan_limits(user)


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






