import frappe
from frappe import _

def get_context(context):
    """
    Fetches the user's current subscription and all available plans
    and adds them to the context for rendering on the portal page.
    """
    context.no_cache = 1
    
    # Redirect guests to login page
    if frappe.session.user == "Guest":
        frappe.local.response["location"] = "/login"
        return

    try:
        # Get the customer linked to the current user
        customer_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")
        frappe.logger().info(f"DEBUG: Customer name for user {frappe.session.user}: {customer_name}")
        
        if not customer_name:
            # Handle cases where user might not be linked to a customer
            context.current_plan = None
            context.current_subscription = None
            frappe.logger().info(f"DEBUG: No customer found for user {frappe.session.user}")
        else:
            # Fetch the user's current subscription plan name from the Customer doc
            current_plan_name = frappe.db.get_value("Customer", customer_name, "custom_tookio_subscription_plan")
            frappe.logger().info(f"DEBUG: Current plan name for customer {customer_name}: {current_plan_name}")
            
            if current_plan_name:
                try:
                    context.current_plan = frappe.get_doc("Subscription Plan", current_plan_name, ignore_permissions=True)
                    frappe.logger().info(f"DEBUG: Successfully loaded plan: {current_plan_name}")
                except Exception as plan_error:
                    frappe.logger().error(f"DEBUG: Error loading plan {current_plan_name}: {plan_error}")
                    context.current_plan = None

                # Get the active subscription details
                subscription_name = frappe.db.get_value(
                    "Subscription",
                    {"party": customer_name, "status": ["in", ["Active", "Past Due Date"]]},
                    "name"
                )
                frappe.logger().info(f"DEBUG: Subscription name for customer {customer_name}: {subscription_name}")
                
                if subscription_name:
                    try:
                        context.current_subscription = frappe.get_doc("Subscription", subscription_name, ignore_permissions=True)
                        frappe.logger().info(f"DEBUG: Successfully loaded subscription: {subscription_name}")
                    except Exception as sub_error:
                        frappe.logger().error(f"DEBUG: Error loading subscription {subscription_name}: {sub_error}")
                        context.current_subscription = None
                else:
                    context.current_subscription = None
            else:
                context.current_plan = None
                context.current_subscription = None

        # Fetch all available subscription plans to display as options
        plans = frappe.get_all(
            "Subscription Plan",
            fields=["name", "custom_item_limits", "custom_shop_limit", "cost", "item"],
            order_by="cost asc",
            ignore_permissions=True
        )
        frappe.logger().info(f"DEBUG: Found {len(plans)} available plans")
        
        # Get description from linked Item doctype for each plan
        context.available_plans = []
        for plan in plans:
            plan_data = plan.copy()
            if plan.get("item"):
                # Fetch description from the linked Item
                item_description = frappe.db.get_value("Item", plan["item"], "description")
                plan_data["description"] = item_description
            else:
                plan_data["description"] = "A great plan for your business."
            context.available_plans.append(plan_data)

    except Exception as e:
        frappe.logger().error(f"DEBUG: Exception caught: {str(e)}")
        frappe.logger().error(f"DEBUG: Exception type: {type(e)}")
        import traceback
        frappe.logger().error(f"DEBUG: Full traceback: {traceback.format_exc()}")
        frappe.log_error(f"Error fetching subscription context for {frappe.session.user}: {e}", "Subscription Page Error")
        context.error = _("Could not load your subscription details at the moment. Please try again later.")
