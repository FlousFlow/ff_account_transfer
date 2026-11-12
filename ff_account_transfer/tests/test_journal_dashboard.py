# -*- coding: utf-8 -*-

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestJournalDashboardBalance(TransactionCase):

    def test_dashboard_balance_uses_linked_account_net(self):
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        self.assertTrue(journal.default_account_id)
        counterpart = self.env['account.account'].search([
            ('id', '!=', journal.default_account_id.id),
            ('deprecated', '=', False),
        ], limit=1)
        self.assertTrue(counterpart)

        move = self.env['account.move'].create({
            'journal_id': journal.id,
            'date': '2026-11-12',
            'line_ids': [
                (0, 0, {
                    'name': 'Dashboard balance test',
                    'account_id': journal.default_account_id.id,
                    'debit': 100.0,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': 'Dashboard balance test',
                    'account_id': counterpart.id,
                    'debit': 0.0,
                    'credit': 100.0,
                }),
            ],
        })
        move.action_post()

        ledger_balance, line_count = journal._get_journal_bank_account_balance(
            domain=[('parent_state', '=', 'posted')]
        )
        dashboard = journal._get_journal_dashboard_data_batched()[journal.id]

        self.assertEqual(ledger_balance, 100.0)
        self.assertEqual(line_count, 1)
        self.assertEqual(dashboard['account_balance'], journal.company_id.currency_id.format(100.0))
        self.assertTrue(dashboard['nb_lines_bank_account_balance'])

    def test_transactions_action_uses_linked_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        action = journal.open_action()

        self.assertEqual(action['res_model'], 'account.move.line')
        self.assertIn(('account_id', '=', journal.default_account_id.id), action['domain'])
        self.assertNotIn(('journal_id', '=', journal.id), action['domain'])
        self.assertEqual(action['context']['search_default_posted'], 1)

    def test_internal_transfer_posts_paired_moves_and_syncs_lifecycle(self):
        bank, cash = self.env['account.journal'].search([
            ('type', 'in', ('bank', 'cash')),
        ], limit=2)
        self.assertEqual(len(bank | cash), 2)
        self.assertTrue(bank.outbound_payment_method_line_ids)
        self.assertTrue(cash.inbound_payment_method_line_ids)

        # The local test chart may not configure payment accounts on manual
        # methods. Configure them for this transaction only, as a real
        # deployment must do before posting payments.
        bank.outbound_payment_method_line_ids[0].payment_account_id = bank.default_account_id
        cash.inbound_payment_method_line_ids[0].payment_account_id = cash.default_account_id

        payment = self.env['account.payment'].create({
            'amount': 250.0,
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': self.env.company.partner_id.id,
            'journal_id': bank.id,
            'payment_method_line_id': bank.outbound_payment_method_line_ids[0].id,
            'destination_journal_id': cash.id,
            'is_internal_transfer': True,
            'date': '2026-11-12',
        })
        payment.action_post()
        paired = payment.paired_internal_transfer_payment_id

        self.assertTrue(paired)
        self.assertEqual(payment.state, 'paid')
        self.assertEqual(paired.state, 'paid')
        self.assertEqual(payment.move_id.state, 'posted')
        self.assertEqual(paired.move_id.state, 'posted')
        self.assertEqual(paired.paired_internal_transfer_payment_id, payment)

        payment.action_cancel()
        self.assertEqual(payment.state, 'canceled')
        self.assertEqual(paired.state, 'canceled')
        payment.action_draft()
        self.assertEqual(payment.state, 'draft')
        self.assertEqual(paired.state, 'draft')
