# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install')
class TestCustomerDebtSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Group definitions
        cls.group_salesman = cls.env.ref('sales_team.group_sale_salesman')
        cls.group_salesman_all = cls.env.ref('sales_team.group_sale_salesman_all_leads')
        cls.group_invoice = cls.env.ref('account.group_account_invoice')

        # Test Sales User (Own documents only, no invoice group)
        cls.sales_user = cls.env['res.users'].create({
            'name': 'Test Salesman Own Only',
            'login': 'test_salesman_own_only@example.com',
            'email': 'test_salesman_own_only@example.com',
            'groups_id': [(6, 0, [cls.group_salesman.id])],
        })

        # Test Sales All Documents User
        cls.sales_all_user = cls.env['res.users'].create({
            'name': 'Test Salesman All Docs',
            'login': 'test_salesman_all_docs@example.com',
            'email': 'test_salesman_all_docs@example.com',
            'groups_id': [(6, 0, [cls.group_salesman_all.id])],
        })

    def test_01_sales_user_own_can_access_wizard(self):
        """Verify Sales User (Own Documents Only) can create & read customer.debt.report.wizard"""
        wizard = self.env['customer.debt.report.wizard'].with_user(self.sales_user).create({
            'number_of_months': 6,
            'report_by': 'partner',
        })
        self.assertTrue(wizard.id, "Sales user should be able to create customer debt wizard")
        self.assertEqual(wizard.with_user(self.sales_user).number_of_months, 6)

    def test_02_sales_user_all_can_access_wizard(self):
        """Verify Sales User (All Documents) can create & read customer.debt.report.wizard"""
        wizard = self.env['customer.debt.report.wizard'].with_user(self.sales_all_user).create({
            'number_of_months': 12,
            'report_by': 'partner',
        })
        self.assertTrue(wizard.id, "Sales All user should be able to create customer debt wizard")
        self.assertEqual(wizard.with_user(self.sales_all_user).number_of_months, 12)

    def test_03_action_and_report_groups(self):
        """Verify report action and window action include sales groups"""
        report_action = self.env.ref('customer_debt_monthly_report.customer_debt_report_xlsx_action')
        window_action = self.env.ref('customer_debt_monthly_report.customer_debt_report_wizard_action')

        self.assertIn(self.group_salesman, report_action.groups_id, "Salesman group should be in report action groups")
        self.assertIn(self.group_salesman, window_action.groups_id, "Salesman group should be in window action groups")
