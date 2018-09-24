# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Model mixins for `lino_xl.lib.invoicing`.

"""

from __future__ import unicode_literals


import logging

import six

logger = logging.getLogger(__name__)

from lino.api import dd
from lino.core.gfks import gfk2lookup

from django.contrib.contenttypes.fields import GenericRelation


class Invoiceable(dd.Model):

    invoiceable_date_field = None

    class Meta:
        abstract = True

    invoicings = GenericRelation(
        dd.plugins.invoicing.item_model,
        content_type_field='invoiceable_type',
        object_id_field='invoiceable_id')

    @classmethod
    def on_analyze(cls, site):
        super(Invoiceable, cls).on_analyze(site)
        de = cls.get_data_elem(cls.invoiceable_date_field)
        def get_invoiceable_date(self):
            return de.value_from_object(self)
        cls.get_invoiceable_date = get_invoiceable_date
        # if isinstance(cls.invoiceable_date_field, six.string_types):
        #     cls.invoiceable_date_field = 
            
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
        return six.text_type(self)

    def get_invoiceable_amount(self):
        return None

    def get_invoiceable_partner(self):
        return None

    def get_invoiceable_payment_term(self):
        return None

    def get_invoiceable_paper_type(self):
        return None

    # def get_invoiceable_date(self):
    #     # return self.invoiceable_date_field.value_from_object(self)
    #     return self.invoiceable_date_field
    #     # return getattr(self, self.invoiceable_date_field)

    @classmethod
    def get_invoiceables_for_plan(cls, plan, partner=None):
        raise NotImplementedError()

    def setup_invoice_item(self, item):
        pass
