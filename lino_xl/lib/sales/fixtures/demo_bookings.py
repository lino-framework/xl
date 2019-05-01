# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


import datetime
from dateutil.relativedelta import relativedelta as delta

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino_xl.lib.vat.mixins import myround
from lino_xl.lib.vat.choicelists import VatAreas, VatRules

# from lino.core.requests import BaseRequest
REQUEST = settings.SITE.login()  # BaseRequest()


def objects():

    TradeTypes = rt.models.ledger.TradeTypes
    #VatRule = rt.models.vat.VatRule
    Journal = rt.models.ledger.Journal
    # Person = rt.models.contacts.Person
    Partner = rt.models.contacts.Partner
    Product = rt.models.products.Product
    VatProductInvoice = rt.models.sales.VatProductInvoice
    InvoiceItem = rt.models.sales.InvoiceItem
    Country = rt.models.countries.Country

    def get_trade_countries(tt):
        areas = set()
        for va in VatAreas.get_list_items():
            if VatRules.get_vat_rule(va, tt, default=False):
                areas.add(va)
        for obj in Country.objects.all():
            if VatAreas.get_for_country(obj) in areas:
                yield obj

    USERS = Cycler(settings.SITE.user_model.objects.all())

    qs = Product.objects.order_by('id')
    # if dd.is_installed('invoicing'):
    if not dd.plugins.ledger.sales_stories:
        return
    PRODUCTS = Cycler(qs)
    JOURNAL_S = Journal.objects.get(ref="SLS")


    # tt = TradeTypes.sales
    # regimes = set()
    # for reg in VatRegimes.get_list_items():
    #     if VatRule.get_vat_rule(tt, reg, default=False):
    #         regimes.add(reg)
    # qs = Partner.objects.filter(vat_regime__in=regimes).order_by('id')
    # assert qs.count() > 0
    # CUSTOMERS = Cycler(qs)
    CUSTOMERS = Cycler(
        Partner.objects.filter(
            country__in=get_trade_countries(
                TradeTypes.sales)).order_by('id'))
    if len(CUSTOMERS) == 0:
        raise Exception("20171006 no customers ({})".format(
            len(list(get_trade_countries(TradeTypes.sales)))))
    
    # CUSTOMERS = Cycler(Person.objects.filter(
    #     gender=dd.Genders.male).order_by('id'))
    # assert Person.objects.count() > 0
    ITEMCOUNT = Cycler(1, 2, 3)
    QUANTITIES = Cycler(15, 10, 8, 4)
    # SALES_PER_MONTH = Cycler(2, 1, 3, 2, 0)
    SALES_PER_MONTH = Cycler(5, 4, 1, 8, 6)

    date = datetime.date(dd.plugins.ledger.start_year, 1, 1)
    end_date = settings.SITE.demo_date(-10)  # + delta(years=-2)
    while date < end_date:

        partner = None
        for i in range(SALES_PER_MONTH.pop()):
            # Every fifth time there are two successive invoices
            # to the same partner.
            if partner is None or i % 5:
                partner = CUSTOMERS.pop()
            invoice = VatProductInvoice(
                journal=JOURNAL_S,
                partner=partner,
                user=USERS.pop(),
                voucher_date=date + delta(days=5 + i),
                entry_date=date + delta(days=5 + i + 1),
                # payment_term=PAYMENT_TERMS.pop(),
            )
            yield invoice
            for j in range(ITEMCOUNT.pop()):
                item = InvoiceItem(
                    voucher=invoice,
                    seqno=j+1,
                    product=PRODUCTS.pop(),
                    qty=QUANTITIES.pop())
                try:
                    item.product_changed(REQUEST)
                except Exception as e:
                    # raise
                    msg = "20171006 {} in ({} {!r})".format(
                        e, invoice.partner, invoice.vat_regime)
                    # raise Exception(msg)
                    dd.logger.warning(msg)
                else:
                    item.before_ui_save(REQUEST)
                    yield item
            invoice.register(REQUEST)
            invoice.save()

        date += delta(months=1)
