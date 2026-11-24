"""Offline security regression tests. No bench, database or network required."""
import ast
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class Denied(Exception):
    pass


class FakeDocument:
    def get(self, key):
        return getattr(self, key, None)

    def get_doc_before_save(self):
        return getattr(self, 'previous', None)


def load_file(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.frappe = types.ModuleType('frappe')
        f = self.frappe
        f.session = types.SimpleNamespace(user='seller')
        f.get_roles = Mock(return_value=['Tookio Seller'])
        f.PermissionError = Denied
        f.db = Mock()
        f.db.escape.side_effect = lambda s: "'" + s.replace("'", "''") + "'"
        f.get_doc = Mock()
        f.new_doc = Mock()
        f.set_user = Mock()
        f.throw = lambda message, exc=Denied: (_ for _ in ()).throw(exc(message))
        f.whitelist = lambda **kwargs: lambda fn: fn
        utils = types.ModuleType('frappe.utils')
        utils.getdate = Mock(return_value='2026-11-24')
        utils.add_months = Mock(return_value='2026-12-24')
        utils.now = Mock(return_value='2026-11-24 12:00:00')
        f.utils = utils
        model = types.ModuleType('frappe.model.document')
        model.Document = FakeDocument
        self.modules = patch.dict(sys.modules, {'frappe': f, 'frappe.utils': utils,
            'frappe.model.document': model})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.security = load_file('security_under_test', 'tookio_shop/security.py')
        self.security_module = patch.dict(sys.modules, {'tookio_shop.security': self.security})
        self.security_module.start()
        self.addCleanup(self.security_module.stop)
        self.controller = load_file('confirmation_under_test',
            'tookio_shop/tookio_shop/doctype/tookio_payment_confirmation/tookio_payment_confirmation.py')

    def claim(self, **values):
        doc = self.controller.TookioPaymentConfirmation()
        defaults = dict(user='seller', status='Pending Verification', verified_by=None,
            verified_date=None, subscription_plan='paid-plan', previous=None)
        defaults.update(values)
        for key, value in defaults.items():
            setattr(doc, key, value)
        return doc

    def api_function(self, name):
        # Compile the actual function body, isolating the large API module's
        # unrelated payment integrations from this offline regression suite.
        tree = ast.parse((ROOT / 'tookio_shop/api.py').read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        node.decorator_list = []
        ns = dict(frappe=self.frappe, require_subscription_owner=self.security.require_subscription_owner,
            ensure_signup_enabled=self.security.ensure_signup_enabled)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(ROOT / 'tookio_shop/api.py'), 'exec'), ns)
        return ns[name], ns

    def test_seller_cannot_verify_own_payment(self):
        for status in ['Verified', 'Rejected']:
            with self.subTest(status=status), self.assertRaises(Denied):
                self.claim(status=status).validate()

    def test_seller_cannot_forge_verifier_or_beneficiary(self):
        for values in [dict(verified_by='Administrator'), dict(verified_date='yesterday'), dict(user='victim')]:
            with self.subTest(values=values), self.assertRaises(Denied):
                self.claim(**values).validate()

    def test_pending_claim_is_allowed_without_upgrade(self):
        doc = self.claim()
        doc.validate()
        doc.on_update()
        self.frappe.get_doc.assert_not_called()
        self.frappe.set_user.assert_not_called()
        self.frappe.db.commit.assert_not_called()

    def test_verified_claim_cannot_be_repurposed(self):
        self.frappe.session.user = 'Administrator'
        original = self.claim(status='Verified')
        for values in [dict(user='victim'), dict(subscription_plan='other-plan'), dict(status='Pending Verification')]:
            updated = dict(status='Verified', previous=original)
            updated.update(values)
            with self.subTest(values=values), self.assertRaises(Denied):
                self.claim(**updated).validate()

    def test_admin_approval_preserves_identity_and_request_transaction(self):
        self.frappe.session.user = 'manager'
        self.frappe.get_roles.return_value = ['System Manager']
        doc = self.claim(status='Verified', previous=self.claim())
        self.frappe.db.exists.return_value = None
        subscription = Mock()
        self.frappe.new_doc.return_value = subscription
        doc.validate()
        doc.on_update()
        self.assertEqual(doc.verified_by, 'manager')
        self.assertEqual(subscription.user, 'seller')
        self.assertEqual(subscription.owner, 'seller')
        subscription.save.assert_called_once_with(ignore_permissions=True)
        self.frappe.set_user.assert_not_called()
        self.frappe.db.commit.assert_not_called()
        self.assertEqual(self.frappe.session.user, 'manager')

    def test_approved_claim_is_not_granted_twice(self):
        self.frappe.session.user = 'Administrator'
        self.claim(status='Verified', previous=self.claim(status='Verified')).on_update()
        self.frappe.new_doc.assert_not_called()
        self.frappe.get_doc.assert_not_called()

    def test_seller_cannot_write_or_read_other_transactions(self):
        own = types.SimpleNamespace(owner='seller')
        other = types.SimpleNamespace(owner='victim')
        for ptype in ['write', 'create', 'delete', 'share', 'export']:
            self.assertFalse(self.security.payment_record_permission(own, ptype, 'seller'))
        self.assertTrue(self.security.payment_record_permission(own, 'read', 'seller'))
        self.assertFalse(self.security.payment_record_permission(other, 'read', 'seller'))
        self.assertFalse(self.security.payment_record_permission(own, 'read', 'Guest'))

    def test_transaction_query_is_scoped(self):
        self.assertIn("`owner` = 'seller'", self.security.payment_record_query('seller'))
        self.assertEqual(self.security.payment_record_query('Guest'), '1=0')
        self.assertEqual(self.security.payment_record_query('Administrator'), '')

    def test_subscription_resolver_rejects_other_user_instead_of_falling_back(self):
        fn, ns = self.api_function('resolve_current_user_subscription')
        self.frappe.get_doc.return_value = types.SimpleNamespace(user='victim')
        ns['get_user_subscription'] = Mock()
        with self.assertRaises(Denied):
            fn('victim-subscription')
        ns['get_user_subscription'].assert_not_called()

    def test_payment_submission_cannot_upgrade_or_auto_verify(self):
        fn, ns = self.api_function('submit_payment_confirmation')
        self.frappe.get_doc.return_value = types.SimpleNamespace(enabled=True)
        doc = Mock(name='claim')
        doc.name = 'claim-1'
        self.frappe.new_doc.return_value = doc
        ns['upgrade_user_subscription'] = Mock()
        result = fn('paid-plan', 'Customer')
        self.assertTrue(result['success'])
        self.assertEqual(doc.status, 'Pending Verification')
        self.assertIsNone(doc.verified_by)
        self.assertIsNone(doc.verified_date)
        ns['upgrade_user_subscription'].assert_not_called()
        self.frappe.set_user.assert_not_called()

    def test_guest_cannot_submit_claim(self):
        self.frappe.session.user = 'Guest'
        fn, _ = self.api_function('submit_payment_confirmation')
        with self.assertRaises(Denied):
            fn('paid-plan', 'Customer')
        self.frappe.new_doc.assert_not_called()

    def test_admin_transaction_access_retains_framework_permission_checks(self):
        other = types.SimpleNamespace(owner='victim')
        self.assertTrue(self.security.payment_record_permission(other, 'write', 'Administrator'))
        self.frappe.get_roles.return_value = ['System Manager']
        self.assertTrue(self.security.payment_record_permission(other, 'write', 'manager'))

    def test_confirmation_access_is_scoped_and_write_is_denied(self):
        doc = self.claim()
        self.assertTrue(self.controller.has_permission(doc, 'read', 'seller'))
        self.assertFalse(self.controller.has_permission(doc, 'write', 'seller'))
        self.assertFalse(self.controller.has_permission(doc, 'read', 'victim'))
        self.assertIn("`user` = 'seller'", self.controller.get_permission_query_conditions('seller'))
        self.assertEqual(self.controller.get_permission_query_conditions('Guest'), '1=0')

    def test_disabled_plan_is_not_accepted(self):
        fn, _ = self.api_function('submit_payment_confirmation')
        self.frappe.get_doc.return_value = types.SimpleNamespace(enabled=False)
        with self.assertRaises(Denied):
            fn('disabled-plan', 'Customer')
        self.frappe.new_doc.assert_not_called()

    def test_guest_user_creation_permission_removed(self):
        import json
        fixtures = json.loads((ROOT / 'tookio_shop/fixtures/custom_docperm.json').read_text())
        rows = [r for r in fixtures if r.get('parent') == 'User' and r.get('role') == 'Guest']
        self.assertTrue(rows)
        self.assertTrue(all(not r.get('create') and not r.get('read') for r in rows))

    def test_mobile_signup_and_completion_honor_signup_shutdown(self):
        core_user = types.ModuleType('frappe.core.doctype.user.user')
        core_user.is_signup_disabled = Mock(return_value=True)
        with patch.dict(sys.modules, {'frappe.core.doctype.user.user': core_user}):
            for name, args in [('request_mobile_signup', ('test@example.invalid', 'Test')),
                    ('complete_mobile_signup', ('old-key', 'new-password'))]:
                fn, _ = self.api_function(name)
                with self.subTest(endpoint=name), self.assertRaises(Denied):
                    fn(*args)
        self.frappe.new_doc.assert_not_called()
        self.frappe.get_doc.assert_not_called()
        self.frappe.db.commit.assert_not_called()

    def test_enabled_signup_is_allowed_by_guard(self):
        core_user = types.ModuleType('frappe.core.doctype.user.user')
        core_user.is_signup_disabled = Mock(return_value=False)
        with patch.dict(sys.modules, {'frappe.core.doctype.user.user': core_user}):
            self.security.ensure_signup_enabled()


if __name__ == '__main__':
    unittest.main()
