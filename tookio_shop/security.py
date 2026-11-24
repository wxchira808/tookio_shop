"""Server-side boundaries for customer-owned and payment records."""

import frappe


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
