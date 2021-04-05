# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Defines referrable names for certain well-known accounts.

These names depend on :attr:`lino_xl.lib.ledger.Plugin.use_pcmn`

Currently used by the :mod:`minimal_ledger
<lino_xl.lib.ledger.fixtures.minimal_ledger>` and :mod:`euvatrates
<lino_xl.lib.vat.fixtures.euvatrates>` fixtures.

"""

raise Exception("No longer used (20171008)")

from django.conf import settings

def pcmnref(ref, pcmn):
    if settings.SITE.plugins.ledger.use_pcmn:
        return pcmn
    return ref

# partner centralization accounts:
CUSTOMERS_ACCOUNT = pcmnref('customers', '4000')
SUPPLIERS_ACCOUNT = pcmnref('suppliers',  '4400')
TAX_OFFICES_ACCOUNT = pcmnref('tax_offices',  '4500')
BANK_PO_ACCOUNT = pcmnref('bank_po',  '4600')

# VAT to declare:
VAT_DUE_ACCOUNT = pcmnref('vat_due',   '4510')
VAT_RETURNABLE_ACCOUNT = pcmnref('vat_returnable',   '4511')
VAT_DEDUCTIBLE_ACCOUT = pcmnref('vat_deductible', '4512')

# declared VAT:
VATDCL_ACCOUNT = pcmnref('vatdcl', '4513')

# financial accounts
BESTBANK_ACCOUNT = pcmnref('bestbank', '5500')
CASH_ACCOUNT = pcmnref('cash', '5700')

PURCHASE_OF_GOODS = pcmnref('goods', '6040')
PURCHASE_OF_SERVICES = pcmnref('services', '6010')
PURCHASE_OF_INVESTMENTS = pcmnref('investments', '6020')

# PO_BESTBANK_ACCOUNT = pcmnref('bestbankpo', '5810')

SALES_ACCOUNT = pcmnref('sales', '7000')

MEMBERSHIP_FEE_ACCOUNT = pcmnref('membership_fee', '7310')
