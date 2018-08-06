# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Model mixins for `lino_xl.lib.invoicing`.

"""

from __future__ import unicode_literals


import logging
logger = logging.getLogger(__name__)

from decimal import Decimal

ZERO = Decimal()

from lino.api import dd, rt
from lino.core.gfks import gfk2lookup

from django.contrib.contenttypes.fields import GenericRelation


class Invoiceable(dd.Model):

    invoiceable_date_field = ''

    class Meta:
        abstract = True

    invoicings = GenericRelation(
        dd.plugins.invoicing.item_model,
        content_type_field='invoiceable_type',
        object_id_field='invoiceable_id')

    def get_invoicings(self, **kwargs):
        item_model = dd.plugins.invoicing.item_model
        # item_model = rt.models.sales.InvoiceItem
        kwargs.update(gfk2lookup(item_model.invoiceable, self))
        return item_model.objects.filter(**kwargs)

    def get_wanted_items(self, ar, invoice, plan, item_model):
        product = self.get_invoiceable_product(plan)
        if not product:
            return []
        i = item_model(voucher=invoice, invoiceable=self,
                       product=product,
                       title=self.get_invoiceable_title(invoice),
                       qty=self.get_invoiceable_qty())
        am = self.get_invoiceable_amount()
        if am is not None:
            i.set_amount(ar, am)
        self.setup_invoice_item(i)
        return [i]

    def get_invoiceable_product(self, plan):
        return None

    def get_invoiceable_qty(self):
        return None

    def get_invoiceable_title(self, invoice=None):
        return unicode(self)

    def get_invoiceable_amount(self):
        return None

    def get_invoiceable_partner(self):
        return None

    def get_invoiceable_payment_term(self):
        return None

    def get_invoiceable_paper_type(self):
        return None

    def get_invoiceable_date(self):
        return getattr(self, self.invoiceable_date_field)

    @classmethod
    def get_invoiceables_for_plan(cls, plan, partner=None):
        raise NotImplementedError()

    def setup_invoice_item(self, item):
        pass
