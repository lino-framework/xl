# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.ledger.utils import HUNDRED
from lino_xl.lib.ledger.choicelists import TradeTypes
from lino_xl.lib.vat.mixins import QtyVatItemBase, VatDocument
from lino_xl.lib.vat.utils import add_vat, remove_vat
from lino_xl.lib.vat.mixins import get_default_vat_regime, myround
from lino_xl.lib.vat.choicelists import VatAreas, VatRules


from lino.api import dd, rt, _

class SalesDocument(VatDocument, Certifiable):
    class Meta:
        abstract = True

    edit_totals = False

    print_items_table = None

    language = dd.LanguageField()
    subject = models.CharField(_("Subject line"), max_length=200, blank=True)
    intro = models.TextField("Introductive Text", blank=True)
    paper_type = dd.ForeignKey('sales.PaperType', null=True, blank=True)
    # channel = Channels.field(default=Channels.as_callable('paper'))

    def get_printable_type(self):
        return self.journal

    def get_print_language(self):
        return self.language or self.partner.language or \
            dd.get_default_language()

    def get_trade_type(self):
        return TradeTypes.sales

    def add_voucher_item(self, product=None, qty=None, **kw):
        Product = rt.models.products.Product
        if product is not None:
            if not isinstance(product, Product):
                product = Product.objects.get(pk=product)
            # if qty is None:
                # qty = Duration(1)
        kw['product'] = product
        kw['qty'] = qty
        return super(SalesDocument, self).add_voucher_item(**kw)

    def get_excerpt_templates(self, bm):
        # Overrides lino_xl.lib.excerpts.mixins.Certifiable.get_excerpt_templates

        pt = self.paper_type or get_paper_type(self.partner)
        if pt and pt.template:
            # print(20190506, pt.template)
            return [pt.template]

def get_paper_type(obj):
    sr = getattr(obj, 'salesrule', None)
    if sr:
        return sr.paper_type


class ProductDocItem(QtyVatItemBase):
    class Meta:
        abstract = True

    product = dd.ForeignKey('products.Product', blank=True, null=True)
    description = dd.RichTextField(
        _("Description"), blank=True, null=True, bleached=True)
    discount = dd.PercentageField(_("Discount"), blank=True, null=True)

    def get_base_account(self, tt):
        # if self.product is None:
        #     return tt.get_base_account()
        return tt.get_product_base_account(self.product)
        # return self.voucher.journal.chart.get_account_by_ref(ref)

    def discount_changed(self, ar=None):
        if not self.product:
            return

        tt = self.voucher.get_trade_type()
        catalog_price = tt.get_catalog_price(self.product)

        if catalog_price is None:
            return
        # assert self.vat_class == self.product.vat_class
        rule = self.get_vat_rule(tt)
        if rule is None:
            return
        va = VatAreas.get_for_country()
        cat_rule = VatRules.get_vat_rule(
            va, tt, get_default_vat_regime(), self.get_vat_class(tt),
            dd.today())
        if cat_rule is None:
            return
        if rule.rate != cat_rule.rate:
            catalog_price = remove_vat(catalog_price, cat_rule.rate)
            catalog_price = add_vat(catalog_price, cat_rule.rate)

        if self.discount is None:
            self.unit_price = myround(catalog_price)
        else:
            self.unit_price = myround(
                catalog_price * (HUNDRED - self.discount) / HUNDRED)
        self.unit_price_changed(ar)

    def product_changed(self, ar=None):
        if self.product:
            self.title = self.product.name
            self.description = self.product.description
            if self.qty is None:
                self.qty = Decimal("1")
            self.discount_changed(ar)

    def full_clean(self):
        super(ProductDocItem, self).full_clean()
        if self.total_incl and not self.product:
            tt = self.voucher.get_trade_type()
            if self.get_base_account(tt) is None:
                raise ValidationError(
                    _("You must specify a product if there is an amount."))


