import frappe
from frappe import _

def get_context(context):
    """
    Tookio Shop is now FREE forever - no subscriptions needed!
    """
    context.no_cache = 1
    context.title = "Tookio Shop - FREE Forever! | No Subscriptions Needed"
    context.meta_description = "Tookio Shop is completely FREE with no subscriptions or payments required. Enjoy unlimited inventory management forever!"

    # Redirect guests to login page
    if frappe.session.user == "Guest":
        frappe.local.response["location"] = "/login"
        return

    # Since app is free, no subscription logic needed
    context.current_plan = None
    context.current_subscription = None
    context.is_free_forever = True
    context.message = "🎉 Tookio Shop is FREE forever! No subscriptions needed."
                
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
