import frappe
from frappe import _
from frappe.utils import random_string, get_url, now_datetime
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def signup(email: str, full_name: str):
    """
    Simple signup: create user with email and full name.
    Send email verification link for the user to set password.
    """
    if not email or not full_name:
        frappe.throw(_("Email and full name are required"))

    email = email.strip().lower()
    full_name = full_name.strip()

    # Check if user already exists
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
        if user.enabled:
            frappe.throw(_("An account with this email already exists"))
        else:
            # Re-enable disabled user and resend verification
            user.enabled = 1
            user.flags.ignore_permissions = True
            user.save()
            send_verification_email(user)
            return {"success": True, "message": _("Verification email sent. Please check your inbox.")}

    # Create new user
    user = frappe.new_doc("User")
    user.email = email
    user.first_name = full_name.split()[0] if full_name else ""
    user.last_name = " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""
    user.enabled = 1
    user.new_password = random_string(20)  # Random password, will be reset via email
    user.user_type = "Website User"
    user.flags.ignore_permissions = True
    user.flags.no_welcome_mail = True  # We'll send our own email
    user.insert()

    # Send verification email
    send_verification_email(user)

    return {"success": True, "message": _("Verification email sent. Please check your inbox to complete signup.")}


def send_verification_email(user):
    """Send email with link to set password"""
    key = random_string(32)
    
    # Store the key
    frappe.db.set_value("User", user.name, "reset_password_key", key)
    
    # Generate the set password link
    link = get_url(f"/shop/set-password?key={key}")
    
    # Send email
    frappe.sendmail(
        recipients=user.email,
        subject=_("Complete your Tookio Shop signup"),
        template="signup_verification",
        args={
            "full_name": user.full_name,
            "link": link,
            "site_name": frappe.local.site or "Tookio Shop"
        },
        header=[_("Complete Your Signup"), "green"],
        now=True
    )


@frappe.whitelist(allow_guest=True)
def set_password(key: str, password: str):
    """
    Set password for user using reset key.
    Called after clicking the verification link.
    """
    if not key or not password:
        frappe.throw(_("Key and password are required"))

    if len(password) < 8:
        frappe.throw(_("Password must be at least 8 characters long"))

    # Find user with this key
    user = frappe.db.get_value("User", {"reset_password_key": key}, "name")
    
    if not user:
        frappe.throw(_("Invalid or expired verification link"))

    # Update password
    update_password(user, password)
    
    # Clear the reset key
    frappe.db.set_value("User", user, "reset_password_key", None)
    
    # Auto-login the user
    frappe.local.login_manager.login_as(user)

    return {"success": True, "message": _("Password set successfully. You are now logged in.")}


@frappe.whitelist(allow_guest=True)
def validate_reset_key(key: str):
    """
    Validate if a reset key is valid.
    Returns user info if valid.
    """
    if not key:
        frappe.throw(_("Key is required"))

    user = frappe.db.get_value(
        "User",
        {"reset_password_key": key},
        ["name", "first_name", "last_name", "email"],
        as_dict=True
    )
    
    if not user:
        frappe.throw(_("Invalid or expired verification link"))

    return {
        "valid": True,
        "email": user.email,
        "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip()
    }
