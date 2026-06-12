import frappe


def get_context(context):
    context.no_cache = 1
    context.title = "Set Tookio Shop Password"

    key = (frappe.form_dict.get("key") or "").strip()
    context.signup_key = key
    context.email = None
    context.invalid_key = False

    if not key:
        context.invalid_key = True
        return context

    context.email = frappe.db.get_value("User", {"reset_password_key": key}, "email")
    if not context.email:
        context.invalid_key = True

    return context
