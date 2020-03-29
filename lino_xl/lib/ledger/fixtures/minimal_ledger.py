# -*- coding: UTF-8 -*-
# Copyright 2012-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _
from lino_xl.lib.ledger.utils import DEBIT, CREDIT
# from lino_xl.lib.ledger import choicelists as pcmn
from lino_xl.lib.ledger.choicelists import CommonAccounts
# from lino.utils import Cycler

#accounts = dd.resolve_app('accounts')
vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')
ledger = dd.resolve_app('ledger')
finan = dd.resolve_app('finan')
bevat = dd.resolve_app('bevat')
eevat = dd.resolve_app('eevat')
bevats = dd.resolve_app('bevats')
#~ partners = dd.resolve_app('partners')


def objects():

    JournalGroups = rt.models.ledger.JournalGroups
    Company = rt.models.contacts.Company

    # JOURNALS

    kw = dict(journal_group=JournalGroups.sales)
    if sales:
        MODEL = sales.VatProductInvoice
    else:
        MODEL = vat.VatAccountInvoice
    kw.update(trade_type='sales')
    # kw.update(ref="OFF", dc=CREDIT)
    # kw.update(printed_name=_("Offer"))
    # kw.update(dd.str2kw('name', _("Offers")))
    # yield MODEL.create_journal(**kw)

    kw.update(ref="SLS", dc=CREDIT)
    kw.update(dd.str2kw('printed_name', _("Invoice")))
    # kw.update(dd.str2kw('name', _("Sales invoices")))
    # kw.update(printed_name=_("Invoice"))
    kw.update(dd.str2kw('name', _("Sales invoices")))
    yield MODEL.create_journal(**kw)

    if dd.plugins.vat.declaration_plugin is None:
        return

    kw.update(ref="SLC", dc=DEBIT)
    kw.update(dd.str2kw('name', _("Sales credit notes")))
    kw.update(dd.str2kw('printed_name', _("Credit note")))
    yield MODEL.create_journal(**kw)

    kw.update(journal_group=JournalGroups.purchases)
    kw.update(trade_type='purchases', ref="PRC")
    kw.update(dd.str2kw('name', _("Purchase invoices")))
    kw.update(dd.str2kw('printed_name', _("Invoice")))
    kw.update(dc=DEBIT)
    if dd.is_installed('ana'):
        yield rt.models.ana.AnaAccountInvoice.create_journal(**kw)
    else:
        yield vat.VatAccountInvoice.create_journal(**kw)

    if finan:

        bestbank = Company(
            name="Bestbank",
            country=dd.plugins.countries.get_my_country())
        yield bestbank

        kw = dict(journal_group=JournalGroups.financial)
        kw.update(dd.str2kw('name', _("Bestbank Payment Orders")))
        kw.update(dd.str2kw('printed_name', _("Payment order")))
        # kw.update(dd.babel_values(
        #     'name', de="Zahlungsaufträge", fr="Ordres de paiement",
        #     en="Payment Orders", et="Maksekorraldused"))
        kw.update(
            trade_type='bank_po',
            partner=bestbank,
            account=CommonAccounts.pending_po.get_object(),
            ref="PMO")
        kw.update(dc=DEBIT)
        yield finan.PaymentOrder.create_journal(**kw)

        kw = dict(journal_group=JournalGroups.financial)
        # kw.update(trade_type='')
        kw.update(dc=CREDIT)
        kw.update(account=CommonAccounts.cash.get_object(), ref="CSH")
        kw.update(dd.str2kw('name', _("Cash book")))
        kw.update(dd.str2kw('printed_name', _("Cash statement")))
        yield finan.BankStatement.create_journal(**kw)

        kw.update(dd.str2kw('name', _("Bestbank")))
        kw.update(dd.str2kw('printed_name', _("Bank statement")))
        kw.update(account=CommonAccounts.best_bank.get_object(), ref="BNK")
        kw.update(dc=CREDIT)
        yield finan.BankStatement.create_journal(**kw)

        kw.update(journal_group=JournalGroups.misc)
        kw.update(account=CommonAccounts.cash.get_object(), ref="MSC")
        kw.update(dc=CREDIT)
        kw.update(dd.str2kw('name', _("Miscellaneous transactions")))
        kw.update(dd.str2kw('printed_name', _("Transaction")))
        yield finan.JournalEntry.create_journal(**kw)

        kw.update(preliminary=True, ref="PRE")
        kw.update(dd.str2kw('name', _("Preliminary transactions")))
        yield finan.JournalEntry.create_journal(**kw)

        kw = dict(journal_group=JournalGroups.wages)
        kw.update(dd.str2kw('name', _("Paychecks")))
        kw.update(dd.str2kw('printed_name', _("Paycheck")))
        kw.update(account=CommonAccounts.cash.get_object(), ref="SAL")
        kw.update(dc=CREDIT)
        yield finan.JournalEntry.create_journal(**kw)



    for m in (bevat, bevats, eevat):
        if not m:
            continue
        kw = dict(journal_group=JournalGroups.vat)
        kw.update(trade_type='taxes')
        kw.update(dd.str2kw('name', _("VAT declarations")))
        kw.update(dd.str2kw('printed_name', _("VAT declaration")))
        kw.update(must_declare=False)
        kw.update(account=CommonAccounts.due_taxes.get_object())
        kw.update(ref=m.DEMO_JOURNAL_NAME, dc=DEBIT)
        yield m.Declaration.create_journal(**kw)

    payments = []
    if finan:
        payments += [finan.BankStatement, finan.JournalEntry,
                     finan.PaymentOrder]

    pending_po = CommonAccounts.pending_po.get_object()
    wages = CommonAccounts.wages.get_object()
    tax_offices = CommonAccounts.tax_offices.get_object()

    MatchRule = rt.models.ledger.MatchRule
    for jnl in ledger.Journal.objects.all():
        if jnl.voucher_type.model in payments:
            yield MatchRule(
                journal=jnl,
                account=CommonAccounts.customers.get_object())
            yield MatchRule(
                journal=jnl,
                account=CommonAccounts.suppliers.get_object())
            if tax_offices:
                yield MatchRule(journal=jnl, account=tax_offices)
            if wages:
                yield MatchRule(journal=jnl, account=wages)
            if jnl.voucher_type.model is not finan.PaymentOrder:
                if pending_po:
                    yield MatchRule(journal=jnl, account=pending_po)
        elif jnl.trade_type:
            a = jnl.trade_type.get_main_account()
            if a:
                yield MatchRule(journal=jnl, account=a)
        # if jnl.voucher_type.model in payments:

    # pending_po = CommonAccounts.pending_po.get_object()
    # if pending_po:
    #     for jnl in ledger.Journal.objects.filter(voucher_type__in=VoucherTypes.finan.BankStatement):
    #         yield MatchRule(journal=jnl, account=pending_po)
