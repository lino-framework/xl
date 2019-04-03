# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Model mixins for `lino_xl.lib.invoicing`.

"""

from __future__ import unicode_literals

import six

from etgen.html import E, join_elems
from lino.api import dd, _, gettext
from lino.core.gfks import gfk2lookup
from lino_xl.lib.ledger.utils import ZERO
from lino_xl.lib.cal.utils import day_and_month

from django.contrib.contenttypes.fields import GenericRelation

MAX_SHOWN = 3  # maximum number of invoiced events shown in
               # invoicing_info

class InvoicingInfo(object):
    invoiced_qty = ZERO
    invoiced_events = 0
    used_events = []
    invoicings = None
    # tariff = None
    invoiceable_product = None
    invoiceable_qty = None
    asset_to_buy = None
    number_of_events = None
    min_asset = None
    max_asset = None

    def __init__(self, enr, max_date=None):
        self.generator = enr
        self.max_date = max_date
        
        max_date = self.max_date or dd.today()
        end_date = enr.get_invoiceable_end_date()
        if end_date:
            max_date = min(max_date, end_date)
        
        product = enr.get_invoiceable_product(max_date)
        # if not product:
        #     # dd.logger.info("20181116c no product")
        #     return
        
        start_date = enr.get_invoiceable_start_date(max_date)

        # if hasattr(product, 'tariff'):
        #     self.tariff = product.tariff
        # self.tariff = getattr(product, 'tariff', None)
        # tariff = product.tariff
        # dd.logger.info("20181116 d %s %s", product, self.tariff)
        # if self.tariff is None or (self.tariff.min_asset is None and
        #                            self.tariff.max_asset) is None:
        tariff = enr.get_invoiceable_tariff(product)
        if tariff is not None:
            self.number_of_events = tariff.number_of_events
            self.min_asset = tariff.min_asset
            self.max_asset = tariff.max_asset
            # every invoiceable creates one invoicing
            # self.invoiceable_product = product
            # self.invoiceable_qty = enr.get_invoiceable_qty()
            # dd.logger.info("20181116 e no tariff")
            # return

        state_field = dd.plugins.invoicing.voucher_model._meta.get_field(
            'state')
        vstates = state_field.choicelist.get_editable_states()
        qs = enr.invoicings.exclude(voucher__state__in=vstates)
        if product is not None:
            qs = qs.filter(product=product)
        self.invoicings = qs

        self.invoiced_events = enr.get_invoiceable_free_events() or 0
            
        for obj in self.invoicings:
            # tariff = getattr(obj.product, 'tariff', None)
            # if tariff:
            if obj.qty is not None:
                self.invoiced_qty += obj.qty
                if self.number_of_events:
                    self.invoiced_events += int(obj.qty * self.number_of_events)
            # history.append("".format())
        # print("20160414", self.invoicings, self.invoiced_qty)

        # min_asset: the minimum number of events a customer should
        # pay in advance

        # max_asset : never invoice more than this number of events
        # per month

        # the asset is what the customer did already pay for.
        # when the asset is negative, we want to invoice a quantity
        # which sets the asset to min_asset.

        # print("20181116 f %s", self.tariff.number_of_events)
        self.used_events = list(enr.get_invoiceable_events(
            start_date, max_date))
        asset = self.invoiced_events - len(self.used_events)
        
        # dd.logger.info(
        #     "20181119 %s %s %s %s",
        #     start_date, max_date, asset, self.min_asset)

        if self.number_of_events:
            # if not start_date:
            #     return
            # print("20160414 c", self.used_events)
            # used_events = qs.count()
            # paid_events = invoiced_qty * fee.number_of_events
            
            if end_date and end_date < max_date and asset >= 0:
                # ticket #1040 : a participant who declared to stop before
                # their asset got negative should not get any invoice for
                # a next asset
                return

            if self.min_asset is None:
                self.asset_to_buy = - asset
            elif asset > self.min_asset:
                return  # nothing to invoice
            else:
                self.asset_to_buy = self.min_asset - asset

            # if asset > 0:
            #     return

            if self.max_asset is not None:
                self.asset_to_buy = min(self.asset_to_buy, self.max_asset)

        elif self.invoiced_qty <= 0:
            self.asset_to_buy = 1
        else:
            return
        
        # qty = self.asset_to_buy * enr.get_invoiceable_qty()
            
        self.invoiceable_product = product
        # self.invoiceable_qty = qty
        # self.asset_to_buy = asset_to_buy


    def format_as_html(self, ar):
        elems = []
        if len(self.used_events) == 0:
            return E.p(gettext("No invoiced events"))
        # used_events = list(self.used_events)
        invoiced = self.used_events[self.invoiced_events:]
        coming = self.used_events[:self.invoiced_events]

        fmt = self.generator.get_invoiceable_event_formatter()
        # def fmt(ev):
        #     return self.generator.format_invoiceable_event(ev, ar)

        if len(invoiced) > 0:
            elems.append("{0} : ".format(_("Invoiced")))
            if len(invoiced) > MAX_SHOWN:
                elems.append("(...) ")
                invoiced = invoiced[-MAX_SHOWN:]
            elems += join_elems(map(fmt, invoiced), sep=', ')
            # s += ', '.join(map(fmt, invoiced))
            # elems.append(E.p(s))
        if len(coming) > 0:
            if len(elems) > 0:
                elems.append(E.br())
            elems.append("{0} : ".format(_("Not invoiced")))
            elems += join_elems(map(fmt, coming), sep=', ')
            # s += ', '.join(map(fmt, coming))
            # elems.append(E.p(s))
        return E.p(*elems)

    def invoice_number(self, voucher):
        # used by lino_voga.courses.Course
        if self.invoicings is None:
            return 0
        n = 1
        for item in self.invoicings:
            n += 1
            if voucher and item.voucher.id == voucher.id:
                break
        # note that voucher.id is None when we are generating the
        # invoice, and then we return the next available number
        return n



class InvoiceGenerator(dd.Model):
    # event_date_field = None

    _invoicing_info = None
    default_invoiceable_qty = 1

    class Meta:
        abstract = True

    invoicings = GenericRelation(
        dd.plugins.invoicing.item_model,
        content_type_field='invoiceable_type',
        object_id_field='invoiceable_id')

    # @classmethod
    # def on_analyze(cls, site):
    #     super(InvoiceGenerator, cls).on_analyze(site)
    #     de = cls.get_data_elem(cls.event_date_field)
    #     def func(self):
    #         return de.value_from_object(self)
    #     cls.get_invoiceable_event_date = func
    #     # if isinstance(cls.invoiceable_date_field, six.string_types):
    #     #     cls.invoiceable_date_field = 
            
    def get_invoicings(self, **kwargs):
        # deprecated. use invoicings instead.
        item_model = dd.plugins.invoicing.item_model
        # item_model = rt.models.sales.InvoiceItem
        kwargs.update(gfk2lookup(item_model.invoiceable, self))
        return item_model.objects.filter(**kwargs)

    def get_last_invoicing(self):
        return self.invoicings.order_by('voucher__voucher_date').last()
        
    def allow_group_invoices(self):
        return True

    def get_invoice_items(self, info, invoice, ar):
        # every generator produces one invoice item per invoicing plan
        # print("20190328", info.invoiceable_product, info.number_of_events)
        if info.invoiceable_product is None:
            return

        kwargs = dict(invoiceable=self, product=info.invoiceable_product)
        
        if info.number_of_events is None:
            qty = info.asset_to_buy * self.get_invoiceable_qty()
            kwargs.update(
                title=self.get_invoiceable_title(), qty=qty)
            yield invoice.add_voucher_item(**kwargs)
            return

        # sell the asset in chunks
        asset_to_buy = info.asset_to_buy
        number = info.invoiced_events // info.number_of_events
        # number = 0
        while asset_to_buy > 0:
            number += 1
            qty = self.get_invoiceable_qty()
            kwargs.update(
                title=self.get_invoiceable_title(number), qty=qty)
            yield invoice.add_voucher_item(**kwargs)
            asset_to_buy -= info.number_of_events

    def get_invoiceable_title(self, number=None):
        return six.text_type(self)

    def compute_invoicing_info(self, max_date=None):
        if self._invoicing_info is None \
           or self._invoicing_info.max_date != max_date:
            self._invoicing_info = InvoicingInfo(self, max_date)
        # assert self._invoicing_info.max_date == max_date
        return self._invoicing_info

    @dd.displayfield(_("Invoicing info"))
    def invoicing_info(self, ar):
        info = self.compute_invoicing_info(dd.today())
        return info.format_as_html(ar)

    # def get_invoiceable_info(self, max_date=None):
    #     return self.compute_invoicing_info(max_date)

    def get_invoiceable_product(self, max_date=None):
        return None

    def get_invoiceable_tariff(self, product=None):
        if product is not None:
            return product.tariff
        return None

    def get_invoiceable_end_date(self):
        return self.end_date

    def get_invoiceable_start_date(self, max_date):
        # don't look at events before this date.
        return None

    def get_invoiceable_events(self, start_date, max_date):
        yield self
    
    def get_invoiceable_event_formatter(self):
        def fmt(ev, ar=None):
            txt = day_and_month(ev.start_date)
            if ar is None:
                return txt
            return ar.obj2html(ev, txt)
        return fmt
    
    def get_invoiceable_free_events(self):
        return 0

    def get_invoiceable_qty(self):
        return self.default_invoiceable_qty

    # def get_invoiceable_amount(self, ie):
    #     return ie.amount
    
    # def get_invoiceable_event_date(self, ie):
    #     return ie.start_date
    
    # def get_invoiceable_amount(self):
    #     return None

    def get_invoiceable_partner(self):
        return None

    def get_invoiceable_payment_term(self):
        return None

    def get_invoiceable_paper_type(self):
        return None

    @classmethod
    def get_generators_for_plan(cls, plan, partner=None):
        return []

    def setup_invoice_item(self, item):
        pass
    
