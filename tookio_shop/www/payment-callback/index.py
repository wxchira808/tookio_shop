import frappe
from frappe import _

def get_context(context):
    """
    Handle payment callback from Pesapal
    """
    context.no_cache = 1
    
    # Get transaction details from URL parameters
    transaction_id = frappe.form_dict.get("transaction_id")
    context.transaction_id = transaction_id
    
    if transaction_id:
        # In a real implementation, you'd verify the payment status with Pesapal here
        context.payment_status = "pending"  # This would come from Pesapal verification
        context.message = _("Your payment is being processed. You will receive an email confirmation shortly.")
    else:
        context.payment_status = "error"
        context.message = _("Payment verification failed. Please contact support.")
