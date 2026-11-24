"""Shop-specific callbacks; never trust a caller's claimed payment result."""

import json
import frappe

from tookio_shop.security import query_mpesa_settlement


@frappe.whitelist(allow_guest=True, methods=["POST"])
def stk_callback():
    try:
        data = json.loads(frappe.request.data or "{}")
        checkout = data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
        if not isinstance(checkout, str) or not checkout or len(checkout) > 140:
            return {"ResultCode": 1, "ResultDesc": "Invalid callback"}
        name = frappe.db.get_value("Mpesa Transaction", {"checkout_request_id": checkout}, "name")
        if not name:
            return {"ResultCode": 1, "ResultDesc": "Transaction not found"}
        frappe.db.sql("SELECT name FROM `tabMpesa Transaction` WHERE name=%s FOR UPDATE", (name,))
        transaction = frappe.get_doc("Mpesa Transaction", name)
        result = query_mpesa_settlement(transaction)
        # Only the authenticated provider response controls stored payment state.
        transaction.result_code = str(result["ResultCode"])
        transaction.result_desc = result.get("ResultDesc", "")
        transaction.status = "Success" if transaction.result_code == "0" else "Failed"
        transaction.callback_received_at = frappe.utils.now()
        transaction.callback_data = json.dumps({"verified_provider_query": result})
        if result.get("MpesaReceiptNumber"):
            transaction.mpesa_receipt_number = result["MpesaReceiptNumber"]
        transaction.save(ignore_permissions=True)
        reference = transaction.account_reference or ""
        if transaction.status == "Success" and "|" in reference and "~" in reference:
            from tookio_shop.api import process_subscription_upgrade

            subscription, intent = reference.split("|", 1)
            process_subscription_upgrade(subscription, intent, transaction.name)
        return {"ResultCode": 0, "ResultDesc": "Callback verified"}
    except Exception:
        # No callback bodies, OAuth tokens or credentials enter the error log.
        frappe.logger().warning("Shop payment callback could not be verified; review required")
        return {"ResultCode": 1, "ResultDesc": "Payment verification requires review"}
