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


"""
Creates fictive demo bookings about monthly sales.

See also:
- :mod:`lino_xl.lib.finan.fixtures.demo_bookings`
- :mod:`lino_xl.lib.ledger.fixtures.demo_bookings`

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


import datetime
from dateutil.relativedelta import relativedelta as delta

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino_xl.lib.vat.mixins import myround

vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')


# from lino.core.requests import BaseRequest
REQUEST = settings.SITE.login()  # BaseRequest()


def objects():

    Journal = rt.models.ledger.Journal
    Person = rt.models.contacts.Person
    Product = rt.models.products.Product

    USERS = Cycler(settings.SITE.user_model.objects.all())

    PRODUCTS = Cycler(Product.objects.order_by('id'))
    JOURNAL_S = Journal.objects.get(ref="SLS")
    CUSTOMERS = Cycler(Person.objects.filter(
        gender=dd.Genders.male).order_by('id'))
    assert Person.objects.count() > 0
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
            invoice = sales.VatProductInvoice(
                journal=JOURNAL_S,
                partner=partner,
                user=USERS.pop(),
                voucher_date=date + delta(days=5 + i),
                entry_date=date + delta(days=5 + i + 1),
                # payment_term=PAYMENT_TERMS.pop(),
            )
            yield invoice
            for j in range(ITEMCOUNT.pop()):
                item = sales.InvoiceItem(
                    voucher=invoice,
                    product=PRODUCTS.pop(),
                    qty=QUANTITIES.pop())
                item.product_changed(REQUEST)
                item.before_ui_save(REQUEST)
                yield item
            invoice.register(REQUEST)
            invoice.save()

        date += delta(months=1)
