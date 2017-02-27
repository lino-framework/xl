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


"""Database models for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from django.db import models
from django.conf import settings
from django.db.models import Q

from lino.mixins.periods import DatePeriod
from lino.mixins import Sequenced
from lino.modlib.system.choicelists import PeriodEvents

from lino.api import dd, rt, _

from .utils import ZERO
from .choicelists import VatClasses, VatRegimes
from .mixins import VatDocument, VatItemBase

from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.mixins import Matching, AccountVoucherItem
from lino_xl.lib.sepa.mixins import Payable
from lino_xl.lib.ledger.choicelists import TradeTypes


TradeTypes.purchases.update(
    base_account_field_name='purchases_account',
    base_account_field_label=_("Purchases Base account"),
    vat_account_field_name='purchases_vat_account',
    vat_account_field_label=_("Purchases VAT account"),
    partner_account_field_name='suppliers_account',
    partner_account_field_label=_("Suppliers account"))


@dd.python_2_unicode_compatible
class VatRule(Sequenced, DatePeriod):
    """A rule which defines how VAT is to be handled for a given invoice
    item.

    Example data see :mod:`lino_xl.lib.vat.fixtures.euvatrates`.

    Database fields:

    .. attribute:: country
    .. attribute:: vat_class

    .. attribute:: vat_regime

        The regime for which this rule applies. Pointer to
        :class:`VatRegimes <lino_xl.lib.vat.choicelists.VatRegimes>`.
    
    .. attribute:: rate
    
        The VAT rate to be applied. Note that a VAT rate of 20 percent is
        stored as `0.20` (not `20`).

    .. attribute:: can_edit

        Whether the VAT amount can be modified by the user. This applies
        only for documents with :attr:`VatTotal.auto_compute_totals` set
        to `False`.

    """
    class Meta:
        verbose_name = _("VAT rule")
        verbose_name_plural = _("VAT rules")

    country = dd.ForeignKey('countries.Country', blank=True, null=True)
    vat_class = VatClasses.field(blank=True)
    vat_regime = VatRegimes.field(blank=True)
    rate = models.DecimalField(default=ZERO, decimal_places=4, max_digits=7)
    can_edit = models.BooleanField(_("Editable amount"), default=True)

    @classmethod
    def get_vat_rule(cls, vat_regime, vat_class, country, date):
        """Return the first VatRule object to be applied for the given
        criteria.

        """
        qs = cls.objects.order_by('seqno')
        qs = qs.filter(Q(country__isnull=True) | Q(country=country))
        if vat_class is not None:
            # qs = qs.filter(Q(vat_class='') | Q(vat_class=vat_class))
            qs = qs.filter(Q(vat_class__in=('', vat_class)))
        if vat_regime is not None:
            qs = qs.filter(
                # Q(vat_regime='') | Q(vat_regime=vat_regime))
                Q(vat_regime__in=('', vat_regime)))
        qs = PeriodEvents.active.add_filter(qs, date)
        if qs.count() > 0:
            return qs[0]
        # rt.show(VatRules)
        msg = _("Found {num} VAT rules for %{context}!)").format(
            num=qs.count(), context=dict(
                vat_regime=vat_regime, vat_class=vat_class,
                country=country.isocode, date=dd.fds(date)))
        msg += " (SQL query was {0})".format(qs.query)
        dd.logger.info(msg)
        # raise Warning(msg)
        return None

    def __str__(self):
        kw = dict(
            vat_regime=self.vat_regime,
            vat_class=self.vat_class,
            rate=self.rate,
            country=self.country, seqno=self.seqno)
        return "{country} {vat_class} {rate}".format(**kw)


class VatAccountInvoice(VatDocument, Payable, Voucher, Matching):
    """An invoice for which the user enters just the bare accounts and
    amounts (not products, quantities, discounts).

    An account invoice does not usually produce a printable
    document. This model is typically used to store incoming purchase
    invoices, but exceptions in both directions are possible: (1)
    purchase invoices can be stored using `purchases.Invoice` if stock
    management is important, or (2) outgoing sales invoice can have
    been created using some external tool and are entered into Lino
    just for the general ledger.

    """
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class InvoiceItem(AccountVoucherItem, VatItemBase):
    """An item of an account invoice.

    """
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
    'contacts.Partner',
    'vat_regime',
    VatRegimes.field(
        blank=True,
        help_text=_("The default VAT regime for \
        sales and purchases of this partner.")))

dd.inject_field(
    'contacts.Company',
    'vat_id',
    models.CharField(_("VAT id"), max_length=200, blank=True))

from .ui import *
