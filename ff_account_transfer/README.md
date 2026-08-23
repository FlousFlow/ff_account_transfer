# Flous Flow Internal Account Transfers

Paired internal transfers between bank and cash journals for **Odoo 18**.

When you post an outbound payment marked as an *Internal Transfer*, the module
automatically creates a paired payment of the opposite type in the destination
journal and cross-references the two payments. The destination account is set
automatically to the company's configured Internal Transfer account.

## Features

- **One-click transfer** from the bank/cash journal dashboard (Accounting
  dashboard → *Internal Transfer*).
- **Automatic paired payment**: posting an outbound internal transfer creates
  the matching inbound payment in the destination journal.
- **Cross-referenced** via `paired_internal_transfer_payment_id` for full
  traceability.
- **Field synchronization**: amount, date and memo stay in sync between the two
  payments.
- **Safe editing**: the amount is locked once the paired payment exists — you
  must cancel and recreate to change it.
- **Arabic translation** included (`ar.po`).

## Installation

1. Copy the `ff_account_transfer` folder to your addons path.
2. Update the apps list and install the module
   (*Invoicing → Internal Transfers*).

Requires the `account` (Invoicing) module.

## Configuration

Make sure the company has an **Internal Transfer Account** set:

*Accounting → Configuration → Settings → Default Accounts → Internal Transfer
Account*.

The source and destination journals must each have at least one payment method
of the relevant type (inbound/outbound).

## Usage

1. Go to the **Accounting dashboard** and open a bank or cash journal.
2. Click **Internal Transfer** (under *New*).
3. Select the destination journal, amount, date and memo.
4. Confirm. The paired payment is created and posted automatically.

You can also list all internal transfers from
*Accounting → Accounting → Internal Transfers*.

## License

LGPL-3. See the `LICENSE` file for the full text.
