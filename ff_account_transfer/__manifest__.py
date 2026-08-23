# -*- coding: utf-8 -*-

{
    'name': 'Flous Flow Internal Account Transfers',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Paired internal transfers between bank and cash journals',
    'description': """
Internal Account Transfers (Flous Flow)
=======================================

This module adds a streamlined internal transfer flow for Odoo 18 Accounting.

When you post an outbound payment marked as an *Internal Transfer*, a paired
payment of the opposite type is automatically created in the destination
journal, and the two payments are cross-referenced. The destination account is
automatically set to the company's configured Internal Transfer account.

Key features
------------
* One-click **Internal Transfer** action from the bank/cash journal dashboard.
* Automatic creation of the paired (inbound/outbound) payment on posting.
* Cross-referencing between the two payments for full traceability.
* Synchronization of amount, date and memo between the paired payments.
* Blocking of amount changes after the paired payment is created.
* Full Arabic translation (ar.po) included.
    """,
    'author': 'Flous Flow / Mohamed Gamal',
    'website': 'https://flousflow.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
