# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals
from __future__ import print_function

from django.db import models
from django.conf import settings
from django.db.models import Q

from lino.mixins.periods import DateRange
from lino.mixins import Sequenced
from lino.modlib.system.choicelists import PeriodEvents

from lino.api import dd, rt, _

from .utils import ZERO
from .choicelists import VatClasses, VatRegimes, VatColumns
from .mixins import VatDocument, VatItemBase

from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.mixins import Matching, AccountVoucherItem
from lino_xl.lib.sepa.mixins import Payable
from lino_xl.lib.ledger.choicelists import TradeTypes


TradeTypes.purchases.update(
    base_account_field_name='purchases_account',
    base_account_field_label=_("Purchases Base account"),
    # vat_account_field_name='purchases_vat_account',
    # vat_account_field_label=_("Purchases VAT account"),
    partner_account_field_name='suppliers_account',
    partner_account_field_label=_("Suppliers account"))


TradeTypes.taxes.update(
    # base_account_field_name='taxes_account',
    # base_account_field_label=_("Taxes Base account"),
    partner_account_field_name='tax_offices_account',
    partner_account_field_label=_("Tax offices account"))


@dd.python_2_unicode_compatible
class VatRule(Sequenced, DateRange):
    class Meta:
        verbose_name = _("VAT rule")
        verbose_name_plural = _("VAT rules")

    country = dd.ForeignKey('countries.Country', blank=True, null=True)
    trade_type = TradeTypes.field(blank=True)
    vat_class = VatClasses.field(blank=True)
    vat_regime = VatRegimes.field(blank=True)
    rate = models.DecimalField(default=ZERO, decimal_places=4, max_digits=7)
    can_edit = models.BooleanField(_("Editable amount"), default=True)
    vat_account = dd.ForeignKey(
        'accounts.Account',
        verbose_name=_("VAT account"),
        related_name="vat_rules_by_account",
        blank=True, null=True)
    vat_returnable = models.BooleanField(
        _("VAT is returnable"), default=False)
    vat_returnable_account = dd.ForeignKey(
        'accounts.Account',
        related_name="vat_rules_by_returnable_account",
        verbose_name=_("VAT returnable account"), blank=True, null=True)

    @classmethod
    def get_vat_rule(cls, trade_type, vat_regime, vat_class=None,
                     country=None, date=None, default=models.NOT_PROVIDED):
        qs = cls.objects.order_by('seqno')
        qs = qs.filter(Q(country__isnull=True) | Q(country=country))
        if trade_type is not None:
            qs = qs.filter(Q(trade_type__in=('', trade_type)))
        if vat_class is not None:
            # qs = qs.filter(Q(vat_class='') | Q(vat_class=vat_class))
            qs = qs.filter(Q(vat_class__in=('', vat_class)))
        if vat_regime is not None:
            qs = qs.filter(
                # Q(vat_regime='') | Q(vat_regime=vat_regime))
                Q(vat_regime__in=('', vat_regime)))
        if date is not None:
            qs = PeriodEvents.active.add_filter(qs, date)
        if qs.count() > 0:
            return qs[0]
        if default is models.NOT_PROVIDED:
            # rt.show(VatRules)
            msg = _("No VAT rule for %{context}!)").format(
                context=dict(
                    vat_regime=vat_regime, vat_class=vat_class,
                    trade_type=trade_type,
                    country=country, date=dd.fds(date)))
            if False:
                msg += " (SQL query was {0})".format(qs.query)
                dd.logger.info(msg)
            else:
                raise Warning(msg)
        return default

    def __str__(self):
        kw = dict(
            trade_type=self.trade_type,
            vat_regime=self.vat_regime,
            vat_class=self.vat_class,
            rate=self.rate,
            country=self.country, seqno=self.seqno)
        return "{trade_type} {country} {vat_class} {rate}".format(**kw)


class VatAccountInvoice(VatDocument, Payable, Voucher, Matching):
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class InvoiceItem(AccountVoucherItem, VatItemBase):
    class Meta:
        verbose_name = _("Account invoice item")
        verbose_name_plural = _("Account invoice items")

    voucher = dd.ForeignKey('vat.VatAccountInvoice', related_name='items')
    title = models.CharField(_("Description"), max_length=200, blank=True)


if False:
    """Install a post_init signal listener for each concrete subclass of
    VatDocument.  The following trick worked...  but best is to store
    it in VatRegime, not per voucher.

    """

    def set_default_item_vat(sender, instance=None, **kwargs):
        instance.item_vat = settings.SITE.get_item_vat(instance)
        # print("20130902 set_default_item_vat", instance)

    @dd.receiver(dd.post_analyze)
    def on_post_analyze(sender, **kw):
        for m in rt.models_by_base(VatDocument):
            dd.post_init.connect(set_default_item_vat, sender=m)
            # print('20130902 on_post_analyze installed receiver for',m)


dd.inject_field(
    'contacts.Partner', 'vat_regime', VatRegimes.field(blank=True))

dd.inject_field(
    'ledger.Movement', 'vat_regime', VatRegimes.field(blank=True))

dd.inject_field(
    'ledger.Movement', 'vat_class', VatClasses.field(blank=True))

# dd.inject_field(
#     'ledger.Movement', 'is_base', models.BooleanField(default=False))

dd.inject_field(
    # 'contacts.Company',
    'contacts.Partner',
    'vat_id',
    models.CharField(_("VAT id"), max_length=200, blank=True))

dd.inject_field('accounts.Account',
                'vat_column',
                VatColumns.field(blank=True, null=True))

