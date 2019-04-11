# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)



from __future__ import print_function
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _
from lino.modlib.checkdata.choicelists import Checker
from lino_xl.lib.ledger.mixins import Matching, AccountVoucherItem
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.sepa.mixins import Payable
from .choicelists import VatClasses, VatRegimes, VatColumns
from .choicelists import VatAreas, VatRules  # make them available for Menu.add_action
from .mixins import VatDocument, VatItemBase


class VatAccountInvoice(VatDocument, Payable, Voucher, Matching):
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    # Override the field to change the text for the purchase invoice.
    your_ref = models.CharField(
        _("Provider's invoice number"), max_length=200, blank=True)


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


def get_vat_regime_choices(country=None, vat_id=None):
    vat_area = VatAreas.get_for_country(country)
    # print("20190405", vat_area)
    for r in VatRegimes.get_list_items():
        if vat_area is None or r.vat_area is None or r.vat_area == vat_area:
            if vat_id or not r.needs_vat_id:
                yield r

@dd.chooser()
def partner_vat_regime_choices(cls, country, vat_id):
    return get_vat_regime_choices(country, vat_id)


dd.inject_action(
    'contacts.Partner',vat_regime_choices=partner_vat_regime_choices)

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


class VatColumnsChecker(Checker):
    # model = 'system.SiteConfig'
    """
    This is an unbound data checker
    (:attr:`lino.modlib.checkdata.Checker.model` is `None`), i.e. the checker
    is unbound, i.e. the problem messages aren't bound to a particular
    database object.
    """

    verbose_name = _("Check VAT columns configuration.")

    def get_checkdata_problems(self, unused_obj, fix=False):
        for vc in VatColumns.get_list_items():
            ca = vc.common_account
            if ca is not None:
                obj = ca.get_object()
                if obj is None:
                    msg = _("No account defined as {} "
                            "(needed by VAT column {})").format(ca, vc.value)
                    yield (True, msg)
                    if fix:
                        obj = ca.create_object()
                        obj.vat_column = vc
                        obj.full_clean()
                        obj.save()
                elif obj.vat_column != vc:
                    msg = _("Account {} must have VAT column {}").format(ca, vc.value)
                    yield (True, msg)
                    if fix:
                        obj.vat_column = vc
                        obj.full_clean()
                        obj.save()

VatColumnsChecker.activate()


