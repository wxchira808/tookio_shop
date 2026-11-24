# Copyright (c) 2025, Tookio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_months, now
from tookio_shop.security import is_security_admin


class TookioPaymentConfirmation(Document):
    def validate(self):
        previous = self.get_doc_before_save()
        if not is_security_admin():
            if (
                frappe.session.user == "Guest"
                or self.user != frappe.session.user
                or self.status != "Pending Verification"
                or self.verified_by
                or self.verified_date
                or (previous and previous.status != "Pending Verification")
                or (previous and previous.user != self.user)
            ):
                frappe.throw("Only administrators can verify payments.", frappe.PermissionError)
        elif self.status in {"Verified", "Rejected"}:
            if not previous or previous.status != self.status:
                self.verified_by = frappe.session.user
                self.verified_date = now()
        # A previously verified claim must not become a fresh entitlement grant
        # by changing its beneficiary or plan or toggling its status.
        if previous and previous.status == "Verified":
            for field in ("user", "subscription_plan", "status"):
                if self.get(field) != previous.get(field):
                    frappe.throw("Verified claims are immutable; create a new claim for review.")

    def on_update(self):
        previous = self.get_doc_before_save()
        if self.status != "Verified" or not self.subscription_plan:
            return
        if not is_security_admin():
            frappe.throw("Only administrators can verify payments.", frappe.PermissionError)
        if previous and previous.status == "Verified":
            return
        user_sub = frappe.db.exists("Tookio User Subscription", {"user": self.user})
        if user_sub:
            doc = frappe.get_doc("Tookio User Subscription", user_sub)
        else:
            doc = frappe.new_doc("Tookio User Subscription")
            doc.user = self.user
            doc.owner = self.user
        doc.current_subscription = self.subscription_plan
        doc.subscription_start_date = getdate()
        doc.subscription_end_date = add_months(getdate(), 1)
        doc.status = "Active"
        doc.save(ignore_permissions=True)
        # Preserve the caller's identity and the enclosing request transaction.


def has_permission(doc, ptype, user):
    if is_security_admin(user):
        return True
    if user == "Guest" or doc.user != user:
        return False
    if ptype in {"read", "select"}:
        return True
    if ptype == "create" and doc.status == "Pending Verification":
        return True
    return False


def get_permission_query_conditions(user=None):
    user = user or frappe.session.user
    if is_security_admin(user):
        return ""
    if user == "Guest":
        return "1=0"
    return "`tabTookio Payment Confirmation`.`user` = " + frappe.db.escape(user)
