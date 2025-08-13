import frappe




def setup_new_user(doc, method):
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

        # 3. Assign Free Plan
        plan_name = "Free Plan"
        if frappe.db.exists("Tookio Subscription Plan", plan_name):
            customer = frappe.get_doc("Customer", customer_name)
            customer.db_set("custom_tookio_subscription_plan", plan_name)

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
    limits = get_user_plan_limits(frappe.session.user)
    count = frappe.db.count("Product", {"owner": frappe.session.user})
    if count >= limits["custom_item_limits"]:
        frappe.throw("Item limit reached. Please upgrade your plan.")

def check_shop_limit(doc, method):
    limits = get_user_plan_limits(frappe.session.user)
    count = frappe.db.count("Shop", {"owner": frappe.session.user})
    if count >= limits["custom_shop_limit"]:
        frappe.throw("Shop limit reached. Please upgrade your plan.")

def prevent_negative_stock(doc, method):
    for item in doc.items:
        # Always fetch latest stock from DB, not from item_stock field
        stock = frappe.db.get_value("Product", item.product, "stock_quantity") or 0
        if item.quantity > stock:
            frappe.throw(f"Not enough stock for {item.product}. Available: {stock}, Requested: {item.quantity}")



