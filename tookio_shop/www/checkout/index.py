import frappe
from frappe import _

def get_context(context):
    """
    Tookio Shop is now FREE forever - redirecting to subscriptions page
    """
    context.no_cache = 1

    # Since app is free, redirect to subscriptions page with free message
    frappe.local.response["location"] = "/subscriptions?free=true"
    return
        
        # Create a draft Sales Invoice for tracking
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = customer_name
        sales_invoice.posting_date = frappe.utils.today()
        sales_invoice.due_date = frappe.utils.add_days(frappe.utils.today(), 30)
        sales_invoice.company = frappe.defaults.get_user_default("Company")
        sales_invoice.currency = "KES"
        
        # Add custom fields for tracking
        sales_invoice.custom_phone_number = phone_number
        sales_invoice.custom_transaction_id = transaction_code
        
        # Add the subscription plan as an invoice item
        sales_invoice.append("items", {
            "item_code": plan.item,
            "item_name": plan.name,
            "description": f"Subscription to {plan.name} - Till Payment Confirmation Code: {transaction_code}",
            "qty": 1,
            "rate": plan.cost,
            "amount": plan.cost
        })
        
        # Add payment details in remarks
        sales_invoice.remarks = f"M-Pesa Till Payment - Till No: 6547212, Phone: {phone_number}, Confirmation Code: {transaction_code}, Date: {frappe.utils.now()}"
        
        # Save as draft (will be manually verified and submitted later)
        sales_invoice.insert(ignore_permissions=True)
        
        # Update customer's subscription plan
        customer.custom_tookio_subscription_plan = plan.name
        customer.save(ignore_permissions=True)
        
        # Create or update subscription record
        existing_subscription = frappe.db.get_value(
            "Subscription", 
            {"party": customer_name}, 
            "name"
        )
        
        # Get plan billing details
        plan_billing = frappe.db.get_value(
            "Subscription Plan", 
            plan.name, 
            ["billing_interval", "billing_interval_count"], 
            as_dict=True
        )
        
        # Calculate proper end date based on plan's billing interval
        start_date = frappe.utils.today()
        if plan_billing and plan_billing.billing_interval == "Year":
            end_date = frappe.utils.add_years(start_date, plan_billing.billing_interval_count or 1)
        elif plan_billing and plan_billing.billing_interval == "Month":
            end_date = frappe.utils.add_months(start_date, plan_billing.billing_interval_count or 1)
        else:
            # Default to 1 year for any plan
            end_date = frappe.utils.add_years(start_date, 1)
        
        if existing_subscription:
            # Try to update existing subscription first
            try:
                subscription = frappe.get_doc("Subscription", existing_subscription)
                subscription.plans = []  # Clear existing plans
                subscription.append("plans", {
                    "plan": plan.name,
                    "qty": 1
                })
                subscription.status = "Active"
                
                subscription.save(ignore_permissions=True)
                
                # Update dates using db_set to bypass validations
                subscription.db_set("current_invoice_start", start_date)
                subscription.db_set("current_invoice_end", end_date)
                subscription.db_set("end_date", end_date)
                
            except Exception as update_error:
                frappe.logger().error(f"Error updating subscription, trying to create new one: {str(update_error)}")
                
                # If update fails, cancel old subscription and create new one
                try:
                    old_subscription = frappe.get_doc("Subscription", existing_subscription)
                    old_subscription.db_set("status", "Cancelled")
                    frappe.logger().info(f"Cancelled old subscription {existing_subscription}")
                except:
                    pass  # If cancelling fails, continue anyway
                
                # Create new subscription
                subscription = frappe.new_doc("Subscription")
                subscription.party_type = "Customer"
                subscription.party = customer_name
                subscription.status = "Active"
                subscription.start_date = start_date
                subscription.end_date = end_date
                subscription.current_invoice_start = start_date
                subscription.current_invoice_end = end_date
                subscription.append("plans", {
                    "plan": plan.name,
                    "qty": 1
                })
                subscription.insert(ignore_permissions=True)
        else:
            # Create new subscription
            subscription = frappe.new_doc("Subscription")
            subscription.party_type = "Customer"
            subscription.party = customer_name
            subscription.status = "Active"
            subscription.start_date = start_date
            subscription.end_date = end_date
            subscription.current_invoice_start = start_date
            subscription.current_invoice_end = end_date
            subscription.append("plans", {
                "plan": plan.name,
                "qty": 1
            })
            subscription.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "message": _("Payment confirmed! Your subscription has been activated."),
            "sales_invoice": sales_invoice.name,
            "subscription": subscription.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Payment Confirmation Error")
        frappe.throw(str(e))
