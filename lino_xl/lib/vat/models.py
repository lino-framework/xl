# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
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

from lino_xl.lib.ledger.utils import ZERO
from .choicelists import VatClasses, VatRegimes, VatColumns, VatAreas, VatRules
from .mixins import VatDocument, VatItemBase

from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.mixins import Matching, AccountVoucherItem
from lino_xl.lib.sepa.mixins import Payable
from lino_xl.lib.ledger.choicelists import TradeTypes


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
    'contacts.Partner',
    'vat_id',
    models.CharField(_("VAT id"), max_length=200, blank=True))

dd.inject_field(
    'ledger.Movement', 'vat_regime', VatRegimes.field(blank=True))

dd.inject_field(
    'ledger.Movement', 'vat_class', VatClasses.field(blank=True))

dd.inject_field('ledger.Account',
                'vat_column',
                VatColumns.field(blank=True, null=True))


