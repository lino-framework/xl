# -*- coding: UTF-8 -*-
# Copyright 2015-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from decimal import Decimal

from django.db import models

from lino.utils import SumCollector
from lino_xl.lib.ledger.mixins import (
    Payable, ProjectRelated, AccountVoucherItem, Matching)
from lino_xl.lib.sepa.mixins import BankAccount
from lino_xl.lib.ledger.models import RegistrableVoucher, VoucherStates
from lino.api import dd, _


class AccountInvoice(BankAccount, Payable, RegistrableVoucher, Matching, ProjectRelated):

    class Meta:
        app_label = 'vatless'
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    state = VoucherStates.field(default='draft')
    amount = dd.PriceField(_("Amount"), blank=True, null=True)

    # _total_fields = set(['amount'])
    # """The list of field names to disable when `edit_totals` is
    # False.
    #
    # """
    #
    # edit_totals = False
    #
    # def disabled_fields(self, ar):
    #     """Disable all three total fields if `edit_totals` is False,
    #     otherwise disable :attr:`total_vat` if
    #     :attr:`VatRule.can_edit` is False.
    #
    #     """
    #     fields = super(AccountInvoice, self).disabled_fields(ar)
    #     if not self.edit_totals:
    #         fields |= self._total_fields
    #     return fields

    def get_partner(self):
        return self.partner or self.project

    def compute_totals(self):
        if self.pk is None:
            return
        base = Decimal()
        for i in self.items.all():
            if i.amount is not None:
                base += i.amount
        self.amount = base

    def get_payable_sums_dict(self):
        tt = self.get_trade_type()
        sums = SumCollector()
        for i in self.items.order_by('seqno'):
            if i.amount:
                b = i.get_base_account(tt)
                if b is None:
                    raise Exception(
                        "No base account for %s (amount is %r)" % (
                            i, i.amount))
                sums.collect(
                    ((b, i.get_ana_account()),
                     i.project or self.project, None, None), i.amount)
        return sums

    def full_clean(self, *args, **kw):
        self.compute_totals()
        super(AccountInvoice, self).full_clean(*args, **kw)

    def before_state_change(self, ar, old, new):
        if new.name == 'registered':
            self.compute_totals()
        elif new.name == 'draft':
            pass
        super(AccountInvoice, self).before_state_change(ar, old, new)


class InvoiceItem(AccountVoucherItem, ProjectRelated):
    """An item of an :class:`AccountInvoice`."""
    class Meta:
        app_label = 'vatless'
        verbose_name = _("Invoice item")
        verbose_name_plural = _("Invoice items")

    voucher = dd.ForeignKey('vatless.AccountInvoice', related_name='items')
    title = models.CharField(_("Description"), max_length=200, blank=True)
    amount = dd.PriceField(_("Amount"), blank=True, null=True)


from .ui import *

# print(VouchersByPartner)
