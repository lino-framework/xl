# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Defines referrable names for certain well-known accounts.

These names depend on :attr:`lino_xl.lib.ledger.Plugin.use_pcmn`

Currently used by the :mod:`minimal_ledger
<lino_xl.lib.ledger.fixtures.minimal_ledger>` and :mod:`euvatrates
<lino_xl.lib.vat.fixtures.euvatrates>` fixtures.

"""

from django.conf import settings

def pcmnref(ref, pcmn):
    if settings.SITE.plugins.ledger.use_pcmn:
        return pcmn
    return ref

CUSTOMERS_ACCOUNT = pcmnref('customers', '4000')
SUPPLIERS_ACCOUNT = pcmnref('suppliers',  '4400')

VAT_DUE_ACCOUNT = pcmnref('vat_due',   '4510')
VAT_RETURNABLE_ACCOUNT = pcmnref('vat_returnable',   '4511')
VAT_DEDUCTIBLE_ACCOUT = pcmnref('vat_deductible', '4512')
VATDCL_ACCOUNT = pcmnref('vatdcl', '4513')

BESTBANK_ACCOUNT = pcmnref('bestbank', '5500')
CASH_ACCOUNT = pcmnref('cash', '5700')

PURCHASE_OF_GOODS = pcmnref('goods', '6040')
PURCHASE_OF_SERVICES = pcmnref('services', '6010')
PURCHASE_OF_INVESTMENTS = pcmnref('investments', '6020')

PO_BESTBANK_ACCOUNT = pcmnref('bestbankpo', '5810')

SALES_ACCOUNT = pcmnref('sales', '7000')

MEMBERSHIP_FEE_ACCOUNT = pcmnref('membership_fee', '7310')
