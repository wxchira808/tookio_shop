import frappe
import json
import uuid
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode

@frappe.whitelist()
def update_subscription_plan(new_plan):
	""" Update the subscription plan for the currently logged-in user. """
	frappe.flags.ignore_permissions = True
	try:
		user = frappe.session.user
		customer_name = frappe.db.get_value("Portal User", {"user": user}, "parent")
		if not customer_name:
			return {"status": "error", "message": "Could not find a customer linked to your user."}
		if not frappe.db.exists("Subscription Plan", new_plan):
			return {"status": "error", "message": f"Plan '{new_plan}' not found."}
		# Update the customer's plan
		frappe.db.set_value("Customer", customer_name, "custom_tookio_subscription_plan", new_plan)
		frappe.db.commit()
		return {"status": "success"}
	except Exception as e:
		frappe.log_error(f"Failed to update subscription for {user} to {new_plan}: {e}")
		return {"status": "error", "message": "An internal error occurred. Please contact support."}
	finally:
		frappe.flags.ignore_permissions = False


@frappe.whitelist()
def initiate_pesapal_payment(plan_name, amount, transaction_id, email, phone, first_name, last_name):
    """
    Initiate payment with Pesapal
    """
    try:
        # Get plan details
        plan = frappe.get_doc("Subscription Plan", plan_name)
        
        # Pesapal credentials (in production, store these in Site Config)
        consumer_key = "qkio1BGGYAXTu2JOfm7XSXNruoZsrqEW"
        consumer_secret = "osGQ364R49cXKeOYSpaOnT++rHs="
        
        # Get access token first
        auth_url = "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
        auth_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        auth_data = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret
        }
        
        auth_response = requests.post(auth_url, json=auth_data, headers=auth_headers)
        
        if auth_response.status_code != 200:
            frappe.log_error(f"Pesapal auth failed: {auth_response.text}", "Pesapal Auth Error")
            return {"status": "error", "message": "Payment service temporarily unavailable."}
        
        token_data = auth_response.json()
        access_token = token_data.get("token")
        
        if not access_token:
            return {"status": "error", "message": "Failed to authenticate with payment service."}
        
        # Prepare payment request
        base_url = frappe.utils.get_url()
        callback_url = f"{base_url}/payment-callback?transaction_id={transaction_id}"
        ipn_url = f"{base_url}/api/method/tookio_shop.api.pesapal_ipn"
        
        payment_data = {
            "id": transaction_id,
            "currency": "KES",
            "amount": float(amount),
            "description": f"Subscription to {plan_name}",
            "callback_url": callback_url,
            "notification_id": ipn_url,
            "billing_address": {
                "email_address": email,
                "phone_number": phone,
                "country_code": "KE",
                "first_name": first_name,
                "last_name": last_name
            }
        }
        
        # Submit order request
        submit_url = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(submit_url, json=payment_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            # Store transaction details in a custom doctype for later retrieval
            # For now, we'll use a simple approach with custom fields in Payment Request
            try:
                customer_name = frappe.db.get_value("Portal User", {"user": frappe.session.user}, "parent")
                
                # Create a simple transaction log
                transaction_log = frappe.get_doc({
                    "doctype": "ToDo",  # Using ToDo as a simple storage for now
                    "description": f"Payment Transaction: {transaction_id}",
                    "reference_type": "Customer",
                    "reference_name": customer_name,
                    "status": "Open",
                    "priority": "Medium",
                    "allocated_to": frappe.session.user,
                    # Store transaction details in description
                    "description": json.dumps({
                        "transaction_id": transaction_id,
                        "plan_name": plan_name,
                        "amount": float(amount),
                        "email": email,
                        "phone": phone,
                        "first_name": first_name,
                        "last_name": last_name,
                        "customer_name": customer_name,
                        "order_tracking_id": result.get("order_tracking_id"),
                        "timestamp": frappe.utils.now()
                    })
                })
                transaction_log.insert(ignore_permissions=True)
                frappe.db.commit()
                
            except Exception as log_error:
                frappe.log_error(f"Failed to store transaction log: {log_error}", "Transaction Log Error")
            
            return {
                "status": "success",
                "redirect_url": result.get("redirect_url"),
                "order_tracking_id": result.get("order_tracking_id"),
                "transaction_id": transaction_id
            }
        else:
            frappe.log_error(f"Pesapal payment request failed: {response.text}", "Pesapal Payment Error")
            return {"status": "error", "message": "Failed to initiate payment. Please try again."}
            
    except Exception as e:
        frappe.log_error(f"Error initiating Pesapal payment: {e}", "Pesapal Integration Error")
        return {"status": "error", "message": "An error occurred while processing your request."}


@frappe.whitelist(allow_guest=True)
def pesapal_ipn():
    """
    Handle Pesapal IPN (Instant Payment Notification)
    """
    try:
        data = frappe.local.form_dict or {}

        # Pesapal will send different parameter names depending on integration.
        # Try common keys first.
        transaction_id = data.get('transaction_id') or data.get('id') or data.get('order_tracking_id')
        status = (data.get('status') or data.get('payment_status') or '').upper()

        frappe.log_error(f"Pesapal IPN payload: {data}", "Pesapal IPN")

        if not transaction_id:
            return {"status": "error", "message": "No transaction_id in IPN"}

        # Locate stored transaction metadata created in initiate_pesapal_payment
        tx = find_transaction_log(transaction_id)

        # If IPN reports a successful payment, call our processing flow
        success_indicators = {"COMPLETED", "PAID", "SUCCESS", "OK"}
        if status in success_indicators:
            if tx:
                process_successful_payment(transaction_id, plan_name=tx.get('plan_name'), customer_email=tx.get('email'), amount=tx.get('amount'))
            else:
                # If we don't have stored metadata, call processing with minimal info
                process_successful_payment(transaction_id)

            return {"status": "success"}

        # For non-successful statuses, just log and return
        frappe.log_error(f"Pesapal IPN not a success for {transaction_id}: {status}", "Pesapal IPN")
        return {"status": "acknowledged", "status_value": status}

    except Exception as e:
        frappe.log_error(f"Error processing Pesapal IPN: {e}", "Pesapal IPN Error")
        return {"status": "error", "message": str(e)}


def process_successful_payment(transaction_id, plan_name=None, customer_email=None, amount=None):
    """
    Process successful payment by creating/updating subscription, creating an explicit Sales Invoice
    (with zero discounts), creating a Payment Entry capped at the invoice outstanding amount, and
    notifying the customer.
    """
    frappe.flags.ignore_permissions = True
    try:
        # Normalize inputs
        if not customer_email:
            customer_email = frappe.session.user
        customer_name = frappe.db.get_value("Portal User", {"user": customer_email}, "parent")
        if not customer_name:
            frappe.log_error(f"Customer not found for email: {customer_email}", "Payment Processing Error")
            return {"status": "error", "message": "Customer not found."}

        customer = frappe.get_doc("Customer", customer_name, ignore_permissions=True)
        if not plan_name:
            frappe.log_error("Plan name not provided for subscription creation", "Payment Processing Error")
            return {"status": "error", "message": "Plan name not provided."}

        plan = frappe.get_doc("Subscription Plan", plan_name, ignore_permissions=True)

        # Determine company for accounts
        company = frappe.defaults.get_user_default("Company") or (frappe.get_all("Company", limit=1) or [{}])[0].get("name")

        # Cancel any existing active subscription for this customer
        existing_subscription = frappe.db.get_value(
            "Subscription",
            {"party": customer_name, "status": ["in", ["Active", "Past Due Date"]]},
            "name"
        )
        if existing_subscription:
            subscription_doc = frappe.get_doc("Subscription", existing_subscription, ignore_permissions=True)
            if subscription_doc.status == "Active":
                subscription_doc.status = "Cancelled"
                subscription_doc.save(ignore_permissions=True)

        # Create new subscription
        subscription = frappe.get_doc({
            "doctype": "Subscription",
            "party_type": "Customer",
            "party": customer_name,
            "subscription_plan": plan_name,
            "start_date": frappe.utils.today(),
            "end_date": frappe.utils.add_months(frappe.utils.today(), 1),
            "current_invoice_start": frappe.utils.today(),
            "current_invoice_end": frappe.utils.add_months(frappe.utils.today(), 1),
            "status": "Active",
            "generate_invoice_at_period_start": 0,
            "generate_new_invoices_past_due_date": 0,
            "cancel_at_period_end": 1,
            "follow_calendar_months": 0,
            "additional_discount_percentage": 0,
            "additional_discount_amount": 0,
            "plans": [{"plan": plan_name, "qty": 1}]
        })

        subscription.insert(ignore_permissions=True)

        # Create Sales Invoice explicitly (no discounts)
        plan_cost = plan.cost or 0
        invoice_items = [
            {
                "doctype": "Sales Invoice Item",
                "item_name": plan.name,
                "description": f"Subscription: {plan.name}",
                "qty": 1,
                "rate": plan_cost,
                "price": plan_cost,
                "income_account": get_default_income_account(),
                "discount_percentage": 0,
                "discount_amount": 0,
            }
        ]

        invoice_doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "company": company,
            "customer": customer_name,
            "posting_date": frappe.utils.today(),
            "due_date": frappe.utils.today(),
            "items": invoice_items,
            "additional_discount_percentage": 0,
            "additional_discount_amount": 0,
            "taxes": [],
            "remarks": f"Subscription invoice for {plan.name}",
        })

        # Compute totals deterministically to avoid unexpected discounts/adjustments
        total = 0
        for it in invoice_doc.items:
            total += (it.get("price") or it.get("rate") or 0) * (it.get("qty") or 1)
        invoice_doc.total = total
        invoice_doc.grand_total = total
        invoice_doc.outstanding_amount = total

        invoice_doc.insert(ignore_permissions=True)
        invoice_doc.submit()

        # Create payment entry (cap allocation to outstanding_amount)
        allocated_amount = invoice_doc.outstanding_amount or invoice_doc.grand_total
        payment_entry = create_payment_entry_for_invoice(invoice_doc, transaction_id, allocated_amount)

        # Update customer record and notify
        frappe.db.set_value("Customer", customer_name, "custom_tookio_subscription_plan", plan_name)
        frappe.db.commit()
        send_subscription_confirmation_email(customer, plan, subscription, invoice_doc.name)

        return {"status": "success", "subscription_name": subscription.name, "invoice_name": invoice_doc.name, "payment_entry": payment_entry.name if payment_entry else None}
    except Exception as e:
        frappe.log_error(f"Error processing successful payment: {e}", "Payment Processing Error")
        return {"status": "error", "message": str(e)}
    finally:
        frappe.flags.ignore_permissions = False


def get_default_receivable_account():
    """Get default receivable account"""
    try:
        company = frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name
        account = frappe.get_value("Company", company, "default_receivable_account")
        return account or "Debtors - TC"  # Fallback account
    except:
        return "Debtors - TC"  # Default fallback


def get_default_cash_account():
    """Get default cash account"""
    try:
        company = frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name
        account = frappe.get_value("Company", company, "default_cash_account")
        return account or "Cash - TC"  # Fallback account
    except:
        return "Cash - TC"  # Default fallback
    


def get_default_income_account():
    """Get default income account for the company"""
    try:
        company = frappe.defaults.get_user_default("Company") or frappe.get_all("Company", limit=1)[0].name
        account = frappe.get_value("Company", company, "default_income_account")
        # Fallbacks in order: company default, common 'Sales - TC', or None
        return account or "Sales - TC"
    except:
        return "Sales - TC"


def create_payment_entry_for_invoice(invoice_doc, transaction_id, allocated_amount=None):
    """Create and submit a Payment Entry for the given invoice.
    If allocated_amount is None or greater than outstanding, use outstanding_amount.
    """
    try:
        alloc = allocated_amount if allocated_amount else invoice_doc.outstanding_amount
        # Ensure we don't allocate more than outstanding
        alloc = min(alloc, invoice_doc.outstanding_amount or invoice_doc.grand_total)

        payment_entry = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": invoice_doc.customer,
            "paid_from": get_default_receivable_account(),
            "paid_to": get_default_cash_account(),
            "paid_amount": alloc,
            "received_amount": alloc,
            "target_exchange_rate": 1.0,
            "reference_no": transaction_id,
            "reference_date": frappe.utils.today(),
            "remarks": f"Payment for invoice {invoice_doc.name}. Transaction ID: {transaction_id}",
            "references": [{
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_doc.name,
                "allocated_amount": alloc
            }]
        })

        payment_entry.insert(ignore_permissions=True)
        payment_entry.submit()
        return payment_entry
    except Exception as e:
        frappe.log_error(f"Error creating payment entry: {e}", "Payment Entry Error")
        return None


def find_transaction_log(transaction_id):
    """Look up the ToDo entry used as a transaction log and return parsed metadata dict or None."""
    try:
        todo = frappe.get_all("ToDo", filters={"description": ["like", f"%{transaction_id}%"]}, limit=1)
        if not todo:
            return None
        todo_doc = frappe.get_doc("ToDo", todo[0].name)
        # We stored JSON in description in initiate_pesapal_payment
        try:
            data = json.loads(todo_doc.description)
            return data
        except Exception:
            # If description isn't JSON, return raw string
            return {"raw_description": todo_doc.description}
    except Exception as e:
        frappe.log_error(f"Error finding transaction log {transaction_id}: {e}", "Transaction Log Error")
        return None


def send_subscription_confirmation_email(customer, plan, subscription, invoice_name):
    """Send confirmation email to customer"""
    try:
        subject = f"Subscription Activated: {plan.name}"
        
        # Calculate next billing date
        next_billing = frappe.utils.add_months(frappe.utils.today(), 1)
        
        message = f"""
        <p>Dear {customer.customer_name},</p>
        
        <p>Your subscription to <strong>{plan.name}</strong> has been successfully activated!</p>
        
        <h3>Subscription Details:</h3>
        <ul>
            <li><strong>Plan:</strong> {plan.name}</li>
            <li><strong>Monthly Cost:</strong> KSh {plan.cost or 0}</li>
            <li><strong>Items Limit:</strong> {plan.custom_item_limits}</li>
            <li><strong>Shops Limit:</strong> {plan.custom_shop_limit}</li>
            <li><strong>Start Date:</strong> {frappe.utils.today()}</li>
            <li><strong>Next Billing:</strong> {next_billing}</li>
        </ul>
        
        <h3>Subscription & Invoice Details:</h3>
        <ul>
            <li><strong>Subscription ID:</strong> {subscription.name}</li>
            <li><strong>First Invoice:</strong> {invoice_name}</li>
            <li><strong>Status:</strong> Active</li>
        </ul>
        
        <h3>Important Information:</h3>
        <ul>
            <li>Your subscription will automatically renew monthly</li>
            <li>Invoices will be generated and sent automatically</li>
            <li>You can manage your subscription from your account dashboard</li>
            <li>To cancel, please contact support before your next billing date</li>
        </ul>
        
        <p>You can now access all the features included in your plan.</p>
        
        <p>Thank you for choosing Tookio Shop!</p>
        
        <p>Best regards,<br>The Tookio Team</p>
        """
        
        frappe.sendmail(
            recipients=[customer.email_id or frappe.session.user],
            subject=subject,
            message=message
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send confirmation email: {e}", "Email Error")


@frappe.whitelist()
def activate_free_plan(plan_name):
	""" Activate a free plan without payment processing """
	frappe.flags.ignore_permissions = True
	try:
		plan = frappe.get_doc("Subscription Plan", plan_name, ignore_permissions=True)
		if plan.cost and plan.cost > 0:
			return {"status": "error", "message": "This is not a free plan. Please use the checkout process."}
		user = frappe.session.user
		customer_name = frappe.db.get_value("Portal User", {"user": user}, "parent")
		if not customer_name:
			return {"status": "error", "message": "Could not find a customer linked to your user."}
		customer = frappe.get_doc("Customer", customer_name, ignore_permissions=True)
		existing_subscription = frappe.db.get_value(
			"Subscription", 
			{"party": customer_name, "status": ["in", ["Active", "Past Due Date"]]}, 
			"name"
		)
		if existing_subscription:
			subscription_doc = frappe.get_doc("Subscription", existing_subscription, ignore_permissions=True)
			if subscription_doc.status == "Active":
				subscription_doc.status = "Cancelled"
				subscription_doc.save(ignore_permissions=True)
		subscription = frappe.get_doc({
			"doctype": "Subscription",
			"party_type": "Customer",
			"party": customer_name,
			"subscription_plan": plan_name,
			"start_date": frappe.utils.today(),
			"end_date": frappe.utils.add_years(frappe.utils.today(), 10),  # Long expiry for free plans
			"current_invoice_start": frappe.utils.today(),
			"current_invoice_end": frappe.utils.add_years(frappe.utils.today(), 10),
			"status": "Active",
			"generate_invoice_at_period_start": 0,
			"generate_new_invoices_past_due_date": 0,
			"cancel_at_period_end": 0,
			"follow_calendar_months": 0,
			"plans": [{
				"plan": plan_name,
				"qty": 1
			}]
		})
		subscription.insert(ignore_permissions=True)
		frappe.db.set_value("Customer", customer_name, "custom_tookio_subscription_plan", plan_name)
		frappe.db.commit()
		send_free_plan_confirmation_email(customer, plan, subscription)
		return {
			"status": "success", 
			"subscription_name": subscription.name,
			"message": f"Free plan '{plan_name}' activated successfully!"
		}
	except Exception as e:
		frappe.log_error(f"Failed to activate free plan {plan_name} for {frappe.session.user}: {e}")
		return {"status": "error", "message": "An internal error occurred. Please contact support."}
	finally:
		frappe.flags.ignore_permissions = False


def send_free_plan_confirmation_email(customer, plan, subscription):
    """Send confirmation email for free plan activation"""
    try:
        subject = f"Free Plan Activated: {plan.name}"
        
        message = f"""
        <p>Dear {customer.customer_name},</p>
        
        <p>Your free subscription to <strong>{plan.name}</strong> has been activated!</p>
        
        <h3>Plan Details:</h3>
        <ul>
            <li><strong>Plan:</strong> {plan.name}</li>
            <li><strong>Cost:</strong> FREE</li>
            <li><strong>Items Limit:</strong> {plan.custom_item_limits}</li>
            <li><strong>Shops Limit:</strong> {plan.custom_shop_limit}</li>
            <li><strong>Start Date:</strong> {frappe.utils.today()}</li>
        </ul>
        
        <h3>Subscription Details:</h3>
        <ul>
            <li><strong>Subscription ID:</strong> {subscription.name}</li>
            <li><strong>Status:</strong> Active</li>
            <li><strong>Billing:</strong> No charges apply</li>
        </ul>
        
        <p>You can now access all the features included in your free plan. Upgrade anytime to unlock additional features!</p>
        
        <p>Thank you for choosing Tookio Shop!</p>
        
        <p>Best regards,<br>The Tookio Team</p>
        """
        
        frappe.sendmail(
            recipients=[customer.email_id or frappe.session.user],
            subject=subject,
            message=message
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send free plan confirmation email: {e}", "Email Error")


@frappe.whitelist()
def check_and_handle_expired_subscriptions():
    """
    Check for expired subscriptions and downgrade to free plan
    This can be called via a scheduled job or manually
    """
    try:
        # Get all expired paid subscriptions
        expired_subscriptions = frappe.get_all(
            "Subscription",
            filters={
                "end_date": ["<", frappe.utils.today()],
                "status": ["in", ["Active", "Past Due Date"]],
                "cancel_at_period_end": 1  # Only manual renewal subscriptions
            },
            fields=["name", "party", "subscription_plan", "end_date"]
        )
        
        # Get free plan name (assuming it's the one with cost = 0)
        free_plan = frappe.db.get_value(
            "Subscription Plan", 
            {"cost": 0}, 
            "name"
        )
        
        if not free_plan:
            frappe.log_error("No free plan found for downgrading expired subscriptions", "Subscription Downgrade Error")
            return {"status": "error", "message": "No free plan configured"}
        
        downgraded_count = 0
        
        for expired_sub in expired_subscriptions:
            try:
                # Cancel the expired subscription
                subscription_doc = frappe.get_doc("Subscription", expired_sub.name, ignore_permissions=True)
                subscription_doc.status = "Cancelled"
                subscription_doc.save(ignore_permissions=True)
                
                # Activate free plan for the customer
                customer_name = expired_sub.party
                activate_free_plan_for_customer(customer_name, free_plan)
                
                # Send expiry notification
                send_subscription_expired_email(customer_name, expired_sub.subscription_plan, free_plan)
                
                downgraded_count += 1
                
            except Exception as e:
                frappe.log_error(f"Failed to downgrade subscription {expired_sub.name}: {e}", "Subscription Downgrade Error")
        
        return {
            "status": "success", 
            "message": f"Processed {downgraded_count} expired subscriptions",
            "downgraded_count": downgraded_count
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking expired subscriptions: {e}", "Subscription Check Error")
        return {"status": "error", "message": str(e)}


def activate_free_plan_for_customer(customer_name, free_plan_name):
    """Helper function to activate free plan for a customer"""
    try:
        # Update customer's subscription plan
        frappe.db.set_value("Customer", customer_name, "custom_tookio_subscription_plan", free_plan_name, ignore_permissions=True)
        
        # Create new free subscription
        free_subscription = frappe.get_doc({
            "doctype": "Subscription",
            "party_type": "Customer",
            "party": customer_name,
            "subscription_plan": free_plan_name,
            "start_date": frappe.utils.today(),
            "end_date": frappe.utils.add_years(frappe.utils.today(), 10),
            "current_invoice_start": frappe.utils.today(),
            "current_invoice_end": frappe.utils.add_years(frappe.utils.today(), 10),
            "status": "Active",
            "generate_invoice_at_period_start": 0,
            "generate_new_invoices_past_due_date": 0,
            "cancel_at_period_end": 0,
            "follow_calendar_months": 0,
            "plans": [{
                "plan": free_plan_name,
                "qty": 1
            }]
        })
        
        free_subscription.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return free_subscription.name
        
    except Exception as e:
        frappe.log_error(f"Failed to activate free plan for {customer_name}: {e}", "Free Plan Activation Error")
        return None


def send_subscription_expired_email(customer_name, expired_plan, new_free_plan):
    """Send email notification when subscription expires"""
    try:
        customer = frappe.get_doc("Customer", customer_name, ignore_permissions=True)
        
        subject = f"Subscription Expired - Switched to Free Plan"
        message = f"""
        <p>Dear {customer.customer_name},</p>
        
        <p>Your subscription to <strong>{expired_plan}</strong> has expired and you have been automatically switched to the <strong>{new_free_plan}</strong>.</p>
        
        <h3>What happens now:</h3>
        <ul>
            <li>You can continue using Tookio Shop with free plan limitations</li>
            <li>To restore your previous features, simply renew your subscription</li>
            <li>Visit your subscription dashboard to upgrade anytime</li>
        </ul>
        
        <h3>To Renew:</h3>
        <ol>
            <li>Log into your account</li>
            <li>Go to the Subscriptions page</li>
            <li>Choose your preferred plan</li>
            <li>Complete the payment process</li>
        </ol>
        
        <p>Thank you for using Tookio Shop!</p>
        
        <p>Best regards,<br>The Tookio Team</p>
        """
        
        frappe.sendmail(
            recipients=[customer.email_id],
            subject=subject,
            message=message
        )
        
    except Exception as e:
        frappe.log_error(f"Failed to send subscription expired email: {e}", "Email Error")


@frappe.whitelist()
def test_create_invoice(plan_name):
    """
    Test function to create subscription - for testing purposes
    """
    try:
        # Set ignore permissions flag for this operation
        frappe.flags.ignore_permissions = True
        
        user = frappe.session.user
        
        # Check if it's a free plan
        plan = frappe.get_doc("Subscription Plan", plan_name, ignore_permissions=True)
        if not plan.cost or plan.cost == 0:
            # Use free plan activation for free plans
            return activate_free_plan(plan_name)
        else:
            # Use paid subscription process for paid plans
            result = process_successful_payment(
                transaction_id=f"TEST-{frappe.utils.now()}",
                plan_name=plan_name,
                customer_email=user,
                amount=plan.cost
            )
            return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # Reset the flag
        frappe.flags.ignore_permissions = False

