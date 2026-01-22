"""
M-Pesa Daraja API Integration for Tookio Shop
Handles STK Push, C2B Webhooks, and payment reconciliation.

Each seller has their own M-Pesa credentials - money goes directly to them!
"""

import frappe
import json
from frappe import _


# ==================== STK PUSH (Lipa Na M-Pesa Online) ====================

@frappe.whitelist(allow_guest=False)
def initiate_stk_push(shop, phone_number, amount, order_reference, description=None):
    """
    Initiate STK Push payment for a specific shop.
    The seller must have configured their M-Pesa settings.
    
    Args:
        shop: Shop docname
        phone_number: Customer phone (will be normalized to 254...)
        amount: Amount to charge
        order_reference: Order/Invoice ID for reconciliation
        description: Transaction description (optional)
    
    Returns:
        dict with success status and checkout_request_id
    """
    from tookio_shop.tookio_shop.doctype.tookio_m_pesa_settings.tookio_m_pesa_settings import get_mpesa_settings_for_shop

    # Verify shop ownership
    shop_doc = frappe.get_doc("Shop", shop)
    if shop_doc.owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("You don't have permission to process payments for this shop"))

    # Get M-Pesa settings for this shop
    mpesa_settings = get_mpesa_settings_for_shop(shop)
    if not mpesa_settings:
        return {
            "success": False,
            "error": "M-Pesa is not configured for this shop. Please add your Daraja API credentials."
        }

    # Initiate STK Push
    result = mpesa_settings.initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference=order_reference,
        description=description
    )

    return result


@frappe.whitelist(allow_guest=False)
def check_stk_status(checkout_request_id):
    """
    Check the status of an STK Push request.
    
    Args:
        checkout_request_id: The CheckoutRequestID from initiate_stk_push
    
    Returns:
        Transaction status
    """
    transaction = frappe.db.get_value(
        "M-Pesa Transaction",
        {"checkout_request_id": checkout_request_id},
        ["name", "status", "mpesa_receipt_number", "result_description"],
        as_dict=True
    )

    if not transaction:
        return {"status": "Not Found", "message": "Transaction not found"}

    return {
        "status": transaction.status,
        "receipt_number": transaction.mpesa_receipt_number,
        "message": transaction.result_description
    }


# ==================== WEBHOOK HANDLERS (Guest Access for Safaricom) ====================

@frappe.whitelist(allow_guest=True, methods=["POST"])
def stk_callback():
    """
    Handle STK Push callback from Safaricom.
    Called when customer completes/cancels the STK prompt.
    
    Uses frappe.enqueue to handle in background for speed.
    """
    try:
        # Get shop from query params
        shop = frappe.form_dict.get("shop")
        
        # Parse callback data
        data = frappe.request.get_data(as_text=True)
        callback_data = json.loads(data) if data else {}

        frappe.logger().info(f"STK Callback received for shop {shop}: {callback_data}")

        # Process in background to respond quickly
        frappe.enqueue(
            "tookio_shop.api.mpesa.process_stk_callback",
            queue="short",
            callback_data=callback_data,
            shop=shop
        )

        # Respond immediately to Safaricom
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    except Exception as e:
        frappe.log_error(f"STK Callback Error: {str(e)}", "M-Pesa STK Callback")
        return {"ResultCode": 1, "ResultDesc": "Error processing callback"}


def process_stk_callback(callback_data, shop):
    """
    Process STK Push callback data in background.
    Updates transaction status and triggers order reconciliation.
    """
    try:
        stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
        
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        # Find the transaction
        transaction_name = frappe.db.get_value(
            "M-Pesa Transaction",
            {"checkout_request_id": checkout_request_id},
            "name"
        )

        if not transaction_name:
            frappe.log_error(f"Transaction not found for {checkout_request_id}", "M-Pesa STK Callback")
            return

        transaction = frappe.get_doc("M-Pesa Transaction", transaction_name)

        # Update with callback data
        transaction.result_code = str(result_code)
        transaction.result_description = result_desc
        transaction.raw_callback_data = json.dumps(callback_data, indent=2)

        if result_code == 0:
            # Success! Extract transaction details
            transaction.status = "Completed"
            
            # Parse callback metadata
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            for item in metadata:
                name = item.get("Name")
                value = item.get("Value")
                
                if name == "MpesaReceiptNumber":
                    transaction.mpesa_receipt_number = value
                elif name == "TransactionDate":
                    # Format: YYYYMMDDHHmmss
                    transaction.transaction_date = parse_mpesa_date(value)
                elif name == "Amount":
                    transaction.amount = value
                elif name == "PhoneNumber":
                    transaction.phone_number = str(value)

            frappe.logger().info(f"M-Pesa payment completed: {transaction.mpesa_receipt_number}")
        else:
            # Failed or cancelled
            transaction.status = "Failed" if result_code != 1032 else "Cancelled"
            frappe.logger().info(f"M-Pesa payment {transaction.status}: {result_desc}")

        transaction.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"STK Callback Processing Error: {str(e)}", "M-Pesa STK Callback")


@frappe.whitelist(allow_guest=True, methods=["POST"])
def c2b_validation():
    """
    C2B Validation URL - called before a C2B payment is processed.
    You can accept or reject the payment here.
    
    Return ResultCode 0 to accept, non-zero to reject.
    """
    try:
        shop = frappe.form_dict.get("shop")
        data = frappe.request.get_data(as_text=True)
        validation_data = json.loads(data) if data else {}

        frappe.logger().info(f"C2B Validation for shop {shop}: {validation_data}")

        # You can add custom validation logic here
        # For example, check if amount matches an existing order
        
        # Accept all payments by default
        return {
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        }

    except Exception as e:
        frappe.log_error(f"C2B Validation Error: {str(e)}", "M-Pesa C2B")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}  # Accept even on error


@frappe.whitelist(allow_guest=True, methods=["POST"])
def c2b_confirmation():
    """
    C2B Confirmation URL - called after a C2B payment is completed.
    This is the main webhook for Paybill/Buy Goods payments.
    
    Creates a transaction record and triggers reconciliation.
    """
    try:
        shop = frappe.form_dict.get("shop")
        data = frappe.request.get_data(as_text=True)
        confirmation_data = json.loads(data) if data else {}

        frappe.logger().info(f"C2B Confirmation for shop {shop}: {confirmation_data}")

        # Process in background
        frappe.enqueue(
            "tookio_shop.api.mpesa.process_c2b_confirmation",
            queue="short",
            confirmation_data=confirmation_data,
            shop=shop
        )

        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    except Exception as e:
        frappe.log_error(f"C2B Confirmation Error: {str(e)}", "M-Pesa C2B")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}


def process_c2b_confirmation(confirmation_data, shop):
    """
    Process C2B confirmation data in background.
    Creates transaction record and links to order via BillRefNumber.
    """
    try:
        # Extract C2B fields
        trans_id = confirmation_data.get("TransID")
        trans_amount = confirmation_data.get("TransAmount")
        bill_ref = confirmation_data.get("BillRefNumber", "")
        phone = confirmation_data.get("MSISDN")
        first_name = confirmation_data.get("FirstName", "")
        middle_name = confirmation_data.get("MiddleName", "")
        last_name = confirmation_data.get("LastName", "")
        org_balance = confirmation_data.get("OrgAccountBalance")
        trans_time = confirmation_data.get("TransTime")
        third_party_id = confirmation_data.get("ThirdPartyTransID", "")

        # Check for duplicate
        if frappe.db.exists("M-Pesa Transaction", {"mpesa_receipt_number": trans_id}):
            frappe.logger().info(f"Duplicate C2B transaction ignored: {trans_id}")
            return

        # Create transaction record
        transaction = frappe.new_doc("M-Pesa Transaction")
        transaction.shop = shop
        transaction.transaction_type = "C2B"
        transaction.status = "Completed"
        transaction.mpesa_receipt_number = trans_id
        transaction.amount = trans_amount
        transaction.phone_number = phone
        transaction.account_reference = bill_ref
        transaction.first_name = first_name
        transaction.middle_name = middle_name
        transaction.last_name = last_name
        transaction.org_account_balance = org_balance
        transaction.third_party_trans_id = third_party_id
        transaction.transaction_date = parse_mpesa_date(trans_time)
        transaction.raw_callback_data = json.dumps(confirmation_data, indent=2)
        
        transaction.insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.logger().info(f"C2B Transaction recorded: {trans_id} for shop {shop}")

        # The transaction's after_insert will try to auto-link to an order

    except Exception as e:
        frappe.log_error(f"C2B Processing Error: {str(e)}", "M-Pesa C2B")


# ==================== UTILITY FUNCTIONS ====================

def parse_mpesa_date(mpesa_timestamp):
    """Convert M-Pesa timestamp (YYYYMMDDHHmmss) to datetime"""
    from datetime import datetime
    
    if not mpesa_timestamp:
        return None
    
    try:
        ts = str(mpesa_timestamp)
        return datetime.strptime(ts, "%Y%m%d%H%M%S")
    except:
        return None


@frappe.whitelist(allow_guest=False)
def get_shop_mpesa_status(shop):
    """
    Check if a shop has M-Pesa configured and enabled.
    Used by frontend to show setup prompts.
    """
    settings = frappe.db.get_value(
        "M-Pesa Settings",
        {"shop": shop},
        ["enabled", "environment", "shortcode"],
        as_dict=True
    )

    if not settings:
        return {
            "configured": False,
            "message": "M-Pesa not configured. Add your Daraja API credentials to receive payments."
        }

    return {
        "configured": True,
        "enabled": settings.enabled,
        "environment": settings.environment,
        "shortcode": settings.shortcode
    }


@frappe.whitelist(allow_guest=False)
def get_recent_transactions(shop, limit=10):
    """
    Get recent M-Pesa transactions for a shop.
    Used in seller dashboard.
    """
    # Verify ownership
    shop_owner = frappe.db.get_value("Shop", shop, "owner")
    if shop_owner != frappe.session.user and "System Manager" not in frappe.get_roles():
        frappe.throw(_("Not authorized"))

    transactions = frappe.get_all(
        "M-Pesa Transaction",
        filters={"shop": shop},
        fields=[
            "name", "phone_number", "amount", "mpesa_receipt_number",
            "status", "transaction_date", "linked_order", "account_reference"
        ],
        order_by="creation desc",
        limit=limit
    )

    return transactions
