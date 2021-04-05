# -*- coding: UTF-8 -*-
# Copyright 2009-2015 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Generates 20 fictive sales invoices, distributed over more than
one month.

"""
from __future__ import unicode_literals

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')
ledger = dd.resolve_app('ledger')

partner_model = settings.SITE.partners_app_label + '.Partner'
Partner = dd.resolve_model(partner_model)

REQUEST = settings.SITE.login()


def objects():

    if False:
        yield sales.InvoicingMode(
            **dd.babel_values(
                'name',
                en='Default', de="Standard", fr="Standard"))

    if ledger:
        Invoice = dd.resolve_model('sales.VatProductInvoice')
        InvoiceItem = dd.resolve_model('sales.InvoiceItem')
        vt = ledger.VoucherTypes.get_for_model(Invoice)
        JOURNALS = Cycler(vt.get_journals())
        if len(JOURNALS.items) == 0:
            raise Exception("20140127 no journals for %s" % vt)
        PARTNERS = Cycler(Partner.objects.all())
        USERS = Cycler(settings.SITE.user_model.objects.all())
        PRODUCTS = Cycler(rt.models.products.Product.objects.all())
        ITEMCOUNT = Cycler(1, 2, 3)
        for i in range(20):
            jnl = JOURNALS.pop()
            invoice = Invoice(
                journal=jnl,
                partner=PARTNERS.pop(),
                user=USERS.pop(),
                date=settings.SITE.demo_date(i-21))
            yield invoice
            for j in range(ITEMCOUNT.pop()):
                item = InvoiceItem(voucher=invoice, product=PRODUCTS.pop())
                item.product_changed(REQUEST)
                item.before_ui_save(REQUEST, None)
                yield item
            invoice.register(REQUEST)
            invoice.save()
