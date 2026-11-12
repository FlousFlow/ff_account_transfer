# -*- coding: utf-8 -*-

from odoo import _, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def open_action(self):
        """Open every journal item affecting the journal's linked account.

        The standard bank/cash dashboard opens bank statements for the
        Transactions button.  That omits POS, sales, transfers and other
        entries when they were posted through another journal but hit this
        journal's linked account.
        """
        self.ensure_one()
        if (
            not self.env.context.get('action_name')
            and self.type in ('bank', 'cash', 'credit')
            and self.default_account_id
        ):
            action = self.env['ir.actions.act_window']._for_xml_id(
                'account.action_account_moves_all_a'
            )
            action.update({
                'name': _('Transactions'),
                'domain': [
                    ('account_id', '=', self.default_account_id.id),
                    ('display_type', 'not in', ('line_section', 'line_note')),
                ],
                'context': {
                    'journal_type': 'general',
                    'search_default_group_by_move': 1,
                    'search_default_posted': 1,
                    'expand': 1,
                },
            })
            return action
        return super().open_action()

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        """Show the posted ledger balance of the journal's linked account.

        Odoo's default dashboard combines the last bank statement with direct
        payments and leaves other posted entries under ``Misc. Operations``.
        That makes an internal transfer (and any other direct journal entry on
        the linked account) appear missing from the journal balance.  The
        journal's linked/default account is the accounting source of truth, so
        use its posted net balance for the main dashboard balance.
        """
        super()._fill_bank_cash_dashboard_data(dashboard_data)

        for journal in self.filtered(lambda j: j.type in ('bank', 'cash', 'credit')):
            if not journal.default_account_id:
                continue

            ledger_balance, line_count = journal._get_journal_bank_account_balance(
                domain=[('parent_state', '=', 'posted')]
            )
            currency = journal.currency_id or journal.company_id.currency_id
            accessible = journal.company_id.id in journal.company_id._accessible_branches().ids

            dashboard_data[journal.id].update({
                'account_balance': currency.format(ledger_balance),
                'nb_lines_bank_account_balance': bool(line_count) and accessible,
            })
