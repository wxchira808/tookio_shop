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
        f.conf = {'encryption_key': 'offline-test-key'}
        f.logger = Mock()
        f.log_error = Mock()
        f.db = Mock()
        f.db.escape.side_effect = lambda s: "'" + s.replace("'", "''") + "'"
        f.get_doc = Mock()
        f.new_doc = Mock()
        f.set_user = Mock()
        f.throw = lambda message, exc=Denied: (_ for _ in ()).throw(exc(message))
        f.whitelist = lambda **kwargs: lambda fn: fn
        utils = types.ModuleType('frappe.utils')
        from datetime import datetime
        utils.now_datetime = Mock(return_value=datetime(2026, 11, 24, 12, 0))
        utils.today = Mock(return_value='2026-11-24')
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
            ensure_signup_enabled=self.security.ensure_signup_enabled,
            require_transaction_owner=self.security.require_transaction_owner,
            authorize_subscription_payment=self.security.authorize_subscription_payment,
            validate_subscription_payment=self.security.validate_subscription_payment,
            verify_mpesa_settlement=self.security.verify_mpesa_settlement)
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

    def payment(self):
        subscription = types.SimpleNamespace(name='sub-1', user='seller')
        transaction = types.SimpleNamespace(name='tx-1', owner='seller', checkout_request_id='checkout-1',
            merchant_request_id='merchant-1', amount=100, account_reference='')
        transaction.account_reference = self.security.authorize_subscription_payment(
            transaction, subscription, 'plan-1', 100)
        return transaction, subscription

    def test_signed_payment_accepts_customer_and_callback_plan_formats(self):
        tx, sub = self.payment()
        for plan in ['plan-1', tx.account_reference.split('|')[1]]:
            self.assertEqual(self.security.validate_subscription_payment(tx, sub, plan), 'plan-1')

    def test_signed_payment_rejects_tampering_and_reuse_on_another_checkout(self):
        for field, value in [('amount', 1), ('checkout_request_id', 'another-checkout'),
                ('merchant_request_id', 'another-merchant'), ('owner', 'victim')]:
            tx, sub = self.payment()
            setattr(tx, field, value)
            with self.subTest(field=field), self.assertRaises(Denied):
                self.security.validate_subscription_payment(tx, sub, 'plan-1')

    def test_unsigned_legacy_payment_requires_manual_review(self):
        tx, sub = self.payment()
        tx.account_reference = 'sub-1|plan-1'
        with self.assertRaises(Denied):
            self.security.validate_subscription_payment(tx, sub, 'plan-1')

    def test_signed_payment_cannot_be_retargeted(self):
        tx, sub = self.payment()
        for target in [types.SimpleNamespace(name='sub-2', user='seller'),
                types.SimpleNamespace(name='sub-1', user='victim')]:
            with self.assertRaises(Denied):
                self.security.validate_subscription_payment(tx, target, 'plan-1')
        with self.assertRaises(Denied):
            self.security.validate_subscription_payment(tx, sub, 'more-expensive-plan')

    def provider_mock(self, result):
        network = types.ModuleType('requests')
        network.RequestException = ConnectionError
        network.get = Mock()
        network.get.return_value.json.return_value = {'access_token': 'offline-token'}
        network.post = Mock()
        network.post.return_value.json.return_value = result
        settings = types.SimpleNamespace(environment='Production', consumer_key='offline-consumer',
            store_number='12345', get_password=Mock(return_value='offline-secret'))
        self.frappe.get_single = Mock(return_value=settings)
        return network

    def test_settlement_requires_fresh_provider_confirmation(self):
        tx, _ = self.payment()
        result = dict(ResultCode='0', CheckoutRequestID='checkout-1', MerchantRequestID='merchant-1')
        network = self.provider_mock(result)
        with patch.dict(sys.modules, {'requests': network}):
            self.security.verify_mpesa_settlement(tx)
        network.get.assert_called_once()
        network.post.assert_called_once()
        self.assertEqual(network.post.call_args.kwargs['timeout'], 15)

    def test_settlement_rejects_failure_and_mismatched_provider_ids(self):
        tx, _ = self.payment()
        for change in [dict(ResultCode='1032'), dict(CheckoutRequestID='other'),
                dict(MerchantRequestID='other')]:
            result = dict(ResultCode='0', CheckoutRequestID='checkout-1', MerchantRequestID='merchant-1')
            result.update(change)
            network = self.provider_mock(result)
            with patch.dict(sys.modules, {'requests': network}), self.assertRaises(Denied):
                self.security.verify_mpesa_settlement(tx)

    def test_network_failure_cannot_confirm_payment(self):
        tx, _ = self.payment()
        network = self.provider_mock({})
        network.post.side_effect = ConnectionError('offline')
        with patch.dict(sys.modules, {'requests': network}), self.assertRaises(Denied):
            self.security.verify_mpesa_settlement(tx)

    def test_settled_payment_is_not_applied_twice(self):
        fn, _ = self.api_function('process_subscription_upgrade')
        self.frappe.get_doc.return_value = types.SimpleNamespace(account_reference='SETTLED:tx-1')
        self.assertTrue(fn('sub-1', 'plan-1', 'tx-1'))
        self.frappe.get_doc.assert_called_once_with('Mpesa Transaction', 'tx-1')
        self.frappe.db.commit.assert_not_called()

    def test_polling_another_customers_payment_is_denied_before_processing(self):
        fn, ns = self.api_function('check_subscription_payment_status')
        self.frappe.get_doc.return_value = types.SimpleNamespace(owner='victim')
        ns['process_subscription_upgrade'] = Mock()
        self.assertEqual(fn('victim-payment')['status'], 'Error')
        ns['process_subscription_upgrade'].assert_not_called()

    def test_guest_callback_applies_only_verified_intent_without_identity_switch(self):
        tx, sub = self.payment()
        tx.db_set = Mock()
        sub.current_subscription = 'old-plan'
        sub.subscription_start_date = None
        sub.subscription_end_date = None
        sub.status = 'Active'
        sub.user_email = 'seller'
        sub.append = Mock()
        sub.save = Mock()
        plan = types.SimpleNamespace(enabled=True, currency='KES', subscription_name='Paid',
            shop_limit=2, products_limit=100, sales_invoice_limit=100, name='plan-1')
        docs = {'Mpesa Transaction': tx, 'Tookio User Subscription': sub, 'Tookio Subscription': plan}
        self.frappe.get_doc.side_effect = lambda dt, name: docs[dt]
        self.frappe.session.user = 'Guest'
        self.frappe.sendmail = Mock()
        fn, ns = self.api_function('process_subscription_upgrade')
        ns['verify_mpesa_settlement'] = Mock()
        self.assertTrue(fn(sub.name, tx.account_reference.split('|')[1], tx.name))
        ns['verify_mpesa_settlement'].assert_called_once_with(tx)
        sub.save.assert_called_once_with(ignore_permissions=True)
        tx.db_set.assert_called_once_with('account_reference', 'SETTLED:tx-1', update_modified=False)
        self.assertEqual(self.frappe.session.user, 'Guest')
        self.frappe.set_user.assert_not_called()

    def test_client_cannot_choose_subscription_payment_amount(self):
        tx, sub = self.payment()
        tx.db_set = Mock()
        fn, ns = self.api_function('initiate_subscription_payment')
        ns['resolve_current_user_subscription'] = Mock(return_value=sub)
        ns['calculate_subscription_upgrade_cost'] = Mock(return_value={'amount_to_pay': 100})
        self.frappe.get_doc.return_value = types.SimpleNamespace(enabled=True, currency='KES',
            subscription_name='Paid')
        self.frappe.get_last_doc = Mock(return_value=tx)
        module = types.ModuleType('tookio_mpesa.utils')
        module.initiate_stk_push_for_till = Mock(return_value={'CheckoutRequestID': 'checkout-1'})
        with patch.dict(sys.modules, {'tookio_mpesa.utils': module}), patch.object(sys, 'path', sys.path.copy()):
            result = fn(sub.name, 'plan-1', '254700000000', amount=1)
        self.assertTrue(result['success'])
        self.assertEqual(module.initiate_stk_push_for_till.call_args.kwargs['amount'], 100)
        signed_reference = tx.db_set.call_args.args[1]
        self.assertIn('plan-1~10000~', signed_reference)

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
