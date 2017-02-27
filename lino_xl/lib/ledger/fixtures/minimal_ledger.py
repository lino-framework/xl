# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""
Creates minimal accounting demo data:

- a minimal accounts chart
- some journals


"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


from django.conf import settings
from lino.api import dd, rt, _
from lino_xl.lib.accounts.utils import DEBIT, CREDIT

accounts = dd.resolve_app('accounts')
vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')
ledger = dd.resolve_app('ledger')
finan = dd.resolve_app('finan')
declarations = dd.resolve_app('declarations')
#~ partners = dd.resolve_app('partners')


def pcmnref(ref, pcmn):
    if settings.SITE.plugins.ledger.use_pcmn:
        return pcmn
    return ref

CUSTOMERS_ACCOUNT = pcmnref('customers', '4000')
SUPPLIERS_ACCOUNT = pcmnref('suppliers',  '4400')

VAT_DUE_ACCOUNT = pcmnref('vat_due',   '4510')
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

current_group = None


def objects():

    JournalGroups = rt.modules.ledger.JournalGroups

    def Group(ref, type, fr, de, en, et=None):
        if et is None:
            et = en
        global current_group
        current_group = accounts.Group(
            ref=ref,
            account_type=accounts.AccountTypes.get_by_name(type),
            **dd.babel_values('name', de=de, fr=fr, en=en, et=et))
        return current_group

    def Account(ref, type, fr, de, en, et, **kw):
        kw.update(dd.babel_values('name', de=de, fr=fr, en=en, et=et))
        return accounts.Account(
            group=current_group,
            ref=ref,
            type=accounts.AccountTypes.get_by_name(type),
            **kw)

    yield Group('10', 'capital', "Capital", "Kapital", "Capital", "Kapitaal")

    yield Group('40', 'assets',
                "Créances commerciales",
                "Forderungen aus Lieferungen und Leistungen",
                "Commercial receivable(?)")

    obj = Account(CUSTOMERS_ACCOUNT, 'assets',
                  "Clients", "Kunden",
                  "Customers", "Kliendid", clearable=True, needs_partner=True)
    yield obj
    if sales:
        settings.SITE.site_config.update(clients_account=obj)

    obj = Account(SUPPLIERS_ACCOUNT, 'liabilities',
                  "Fournisseurs",
                  "Lieferanten", "Suppliers", "Hankijad",
                  clearable=True, needs_partner=True)
    yield obj
    if vat:
        settings.SITE.site_config.update(suppliers_account=obj)

    yield Group('45', 'assets', "TVA à payer",
                "Geschuldete MWSt", "VAT to pay", "Käibemaksukonto")
    obj = Account(VAT_DUE_ACCOUNT, 'incomes',
                  "TVA due",
                  "Geschuldete MWSt",
                  "VAT due", "Käibemaks maksta", clearable=True)
    yield obj
    if sales:
        settings.SITE.site_config.update(sales_vat_account=obj)

    obj = Account(
        VAT_DEDUCTIBLE_ACCOUT, 'assets',
        "TVA déductible",
        "Abziehbare MWSt",
        "VAT deductible", "Enammakstud käibemaks",
        clearable=True)
    yield obj
    if ledger:
        settings.SITE.site_config.update(purchases_vat_account=obj)

    # PCMN 55
    yield Group('55', 'assets',
                "Institutions financières", "Finanzinstitute", "Banks")
    yield Account(BESTBANK_ACCOUNT, 'bank_accounts', "Bestbank",
                  "Bestbank", "Bestbank", "Parimpank")
    yield Account(CASH_ACCOUNT, 'bank_accounts', "Caisse", "Kasse",
                  "Cash", "Sularaha")
    yield Group('58', 'assets',
                "Transactions en cours", "Laufende Transaktionen",
                "Running transactions")
    yield Account(PO_BESTBANK_ACCOUNT, 'bank_accounts',
                  "Ordres de paiement Bestbank",
                  "Zahlungsaufträge Bestbank",
                  "Payment Orders Bestbank",
                  "Maksekorraldused Parimpank", clearable=True)

    # TODO: use another account type than bank_accounts:
    yield Account(VATDCL_ACCOUNT, 'bank_accounts',
                  "TVA à declarer",
                  "MWSt zu deklarieren",
                  "VAT to declare", "Käibemaks deklareerimata")

    yield Group('6', 'expenses', u"Charges", u"Aufwendungen", "Expenses", "Kulud")
    yield Account(PURCHASE_OF_GOODS, 'expenses',
                  "Achat de marchandise",
                  "Wareneinkäufe",
                  "Purchase of goods",
                  "Varade soetamine",
                  purchases_allowed=True)
    yield Account(PURCHASE_OF_SERVICES, 'expenses',
                  "Services et biens divers",
                  "Dienstleistungen",
                  "Purchase of services",
                  "Teenuste soetamine",
                  purchases_allowed=True)
    yield Account(PURCHASE_OF_INVESTMENTS, 'expenses',
                  "Investissements", "Anlagen",
                  "Purchase of investments", "Investeeringud",
                  purchases_allowed=True)

    yield Group('7', 'incomes', "Produits", "Erträge", "Revenues", "Tulud")
    obj = Account(SALES_ACCOUNT, 'incomes',
                  "Ventes", "Verkäufe", "Sales", "Müük",
                  sales_allowed=True)
    obj = Account(MEMBERSHIP_FEE_ACCOUNT, 'incomes',
                  "Cotisation", "Mitgliedsbeitrag",
                  "Membership fee", "Liikmemaks",
                  sales_allowed=True, default_amount=15)
    yield obj
    if sales:
        settings.SITE.site_config.update(sales_account=obj)

    # JOURNALS

    kw = dict(journal_group=JournalGroups.sales)
    if sales:
        MODEL = sales.VatProductInvoice
    else:
        MODEL = vat.VatAccountInvoice
    kw.update(trade_type='sales')
    kw.update(ref="SLS", dc=DEBIT)
    kw.update(printed_name=_("Invoice"))
    kw.update(dd.str2kw('name', _("Sales invoices")))
    yield MODEL.create_journal(**kw)

    kw.update(ref="SLC", dc=CREDIT)
    kw.update(dd.str2kw('name', _("Sales credit notes")))
    kw.update(printed_name=_("Credit note"))
    yield MODEL.create_journal(**kw)

    kw.update(journal_group=JournalGroups.purchases)
    kw.update(trade_type='purchases', ref="PRC")
    kw.update(dd.str2kw('name', _("Purchase invoices")))
    kw.update(dc=CREDIT)
    yield vat.VatAccountInvoice.create_journal(**kw)

    if finan:
        kw.update(journal_group=JournalGroups.financial)
        kw.update(dd.str2kw('name', _("Payment Orders")))
        # kw.update(dd.babel_values(
        #     'name', de="Zahlungsaufträge", fr="Ordres de paiement",
        #     en="Payment Orders", et="Maksekorraldused"))
        kw.update(
            trade_type='purchases',
            account=PO_BESTBANK_ACCOUNT,
            ref="PMO")
        kw.update(dc=CREDIT)
        yield finan.PaymentOrder.create_journal(**kw)

        kw.update(journal_group=JournalGroups.financial)
        kw.update(trade_type='')
        kw.update(dc=DEBIT)
        kw.update(account=CASH_ACCOUNT, ref="CSH")
        kw.update(dd.str2kw('name', _("Cash")))
        # kw = dd.babel_values(
        #     'name', en="Cash",
        #     de="Kasse", fr="Caisse",
        #     et="Kassa")
        yield finan.BankStatement.create_journal(**kw)

        kw.update(journal_group=JournalGroups.financial)
        kw.update(dd.str2kw('name', _("Bestbank")))
        kw.update(account=BESTBANK_ACCOUNT, ref="BNK")
        kw.update(dc=DEBIT)
        yield finan.BankStatement.create_journal(**kw)

        kw.update(journal_group=JournalGroups.financial)
        kw.update(dd.str2kw('name', _("Miscellaneous Journal Entries")))
        # kw = dd.babel_values(
        #     'name', en="Miscellaneous Journal Entries",
        #     de="Diverse Buchungen", fr="Opérations diverses",
        #     et="Muud operatsioonid")
        kw.update(account=CASH_ACCOUNT, ref="MSC")
        kw.update(dc=DEBIT)
        yield finan.JournalEntry.create_journal(**kw)

    if declarations:
        kw = dict(journal_group=JournalGroups.financial)
        kw.update(dd.str2kw('name', _("VAT declarations")))
        # kw = dd.babel_values(
        #     'name', en="VAT declarations",
        #     de="MWSt-Erklärungen", fr="Déclarations TVA",
        #     et="Käibemaksudeklaratsioonid")
        kw.update(account=VATDCL_ACCOUNT, ref="VAT", dc=None)
        yield declarations.Declaration.create_journal(**kw)

    payments = []
    if finan:
        payments += [finan.BankStatement, finan.JournalEntry,
                     finan.PaymentOrder]
    
    MatchRule = rt.modules.ledger.MatchRule
    for jnl in ledger.Journal.objects.all():
        if jnl.voucher_type.model in payments:
            yield MatchRule(
                journal=jnl,
                account=settings.SITE.site_config.clients_account)
            yield MatchRule(
                journal=jnl,
                account=settings.SITE.site_config.suppliers_account)
            a = settings.SITE.site_config.wages_account
            if a:
                yield MatchRule(journal=jnl, account=a)
        elif jnl.trade_type:
            a = jnl.trade_type.get_partner_account()
            if a:
                yield MatchRule(journal=jnl, account=a)
