"""Server-side boundaries for customer-owned and payment records."""

import frappe
import base64
import hashlib
import hmac
from decimal import Decimal, InvalidOperation


def ensure_signup_enabled():
    from frappe.core.doctype.user.user import is_signup_disabled

    if is_signup_disabled():
        frappe.throw("New account registration is temporarily disabled.", frappe.PermissionError)


def is_security_admin(user=None):
    user = user or frappe.session.user
    return user != "Guest" and (
        user == "Administrator" or "System Manager" in frappe.get_roles(user)
    )


def require_subscription_owner(doc):
    # Customer API methods must never resolve another customer's subscription,
    # even for a caller who has other administrative roles.
    if frappe.session.user == "Guest" or doc.user != frappe.session.user:
        frappe.throw("You can only access your own subscription.", frappe.PermissionError)
    return doc


def payment_record_permission(doc, ptype, user):
    if is_security_admin(user):
        return True  # The framework still checks role and permission levels.
    if user == "Guest" or ptype not in {"read", "select"}:
        return False
    return doc.owner == user


def payment_record_query(user=None):
    user = user or frappe.session.user
    if is_security_admin(user):
        return ""
    if user == "Guest":
        return "1=0"
    return "`tabMpesa Transaction`.`owner` = " + frappe.db.escape(user)


def require_transaction_owner(transaction):
    if frappe.session.user == "Guest" or transaction.owner != frappe.session.user:
        frappe.throw("You can only access your own payments.", frappe.PermissionError)


def _payment_signature(transaction, subscription, plan, cents):
    key = frappe.conf.get("encryption_key")
    if not key:
        frappe.throw("Payment authorization is not configured.")
    payload = "\n".join(str(x) for x in (
        transaction.name, transaction.checkout_request_id, transaction.merchant_request_id,
        transaction.owner, subscription.name, subscription.user, plan, cents,
    ))
    return hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]


def authorize_subscription_payment(transaction, subscription, plan, amount):
    require_subscription_owner(subscription)
    require_transaction_owner(transaction)
    if any(c in plan for c in "|~\n"):
        frappe.throw("Unsupported subscription identifier.")
    cents = int(Decimal(str(amount)) * 100)
    if cents <= 0:
        frappe.throw("This upgrade requires administrator review.")
    signature = _payment_signature(transaction, subscription, plan, cents)
    reference = f"{subscription.name}|{plan}~{cents}~{signature}"
    if len(reference) > 140:
        frappe.throw("Payment reference is too long.")
    return reference


def validate_subscription_payment(transaction, subscription, requested_plan):
    """Bind a settlement to the server-priced intent, payer and checkout ID."""
    try:
        reference, intent = transaction.account_reference.split("|", 1)
        plan, raw_cents, signature = intent.rsplit("~", 2)
        cents = int(raw_cents)
        amount = Decimal(str(transaction.amount))
    except (ValueError, TypeError, AttributeError, InvalidOperation):
        frappe.throw("This payment requires administrator review.", frappe.PermissionError)
    if (
        reference != subscription.name or transaction.owner != subscription.user
        or requested_plan not in (plan, intent) or cents <= 0
        or not amount.is_finite() or amount * 100 != cents
        or not hmac.compare_digest(signature, _payment_signature(transaction, subscription, plan, cents))
    ):
        frappe.throw("Payment authorization does not match this subscription.", frappe.PermissionError)
    return plan


def query_mpesa_settlement(transaction):
    """Independently query Daraja; callback JSON and local status are not proof."""
    import requests
    from frappe.utils import now_datetime

    settings = frappe.get_single("Tookio Mpesa Settings")
    if settings.environment != "Production":
        frappe.throw("Production payment verification is required.")
    try:
        token_response = requests.get(
            "https://api.safaricom.co.ke/oauth/v1/generate",
            params={"grant_type": "client_credentials"},
            auth=(settings.consumer_key.strip(), settings.get_password("consumer_secret").strip()),
            timeout=15,
        )
        token_response.raise_for_status()
        token = token_response.json()["access_token"]
        timestamp = now_datetime().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{settings.store_number}{settings.get_password('passkey')}{timestamp}".encode()
        ).decode()
        response = requests.post(
            "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query",
            json={"BusinessShortCode": settings.store_number, "Password": password,
                  "Timestamp": timestamp, "CheckoutRequestID": transaction.checkout_request_id},
            headers={"Authorization": f"Bearer {token}"}, timeout=15,
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, KeyError, TypeError, ValueError, AttributeError):
        frappe.throw("Payment verification is unavailable; no upgrade was applied.")
    if (
        result.get("ResultCode") is None
        or result.get("CheckoutRequestID") != transaction.checkout_request_id
        or result.get("MerchantRequestID") != transaction.merchant_request_id
    ):
        frappe.throw("The payment provider has not confirmed this payment.", frappe.PermissionError)
    return result


def verify_mpesa_settlement(transaction):
    result = query_mpesa_settlement(transaction)
    if str(result.get("ResultCode")) != "0":
        frappe.throw("The payment provider has not confirmed this payment.", frappe.PermissionError)
