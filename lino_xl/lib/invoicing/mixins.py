# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
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
    """Mixin for things that are "invoiceable", i.e. for which a customer
    is going to receive an invoice.

    .. attribute:: invoice

    .. attribute:: invoicings

        A simple `GenericRelation
        <https://docs.djangoproject.com/ja/1.9/ref/contrib/contenttypes/#reverse-generic-relations>`_
        to all invoice items pointing to this enrolment.

        This is preferred over :meth:`get_invoicings`.

    """

    invoiceable_date_field = ''
    """The name of the field which holds the invoiceable date.  Must be
    set by subclasses.

    """

    class Meta:
        abstract = True

    # invoice = dd.ForeignKey('sales.VatProductInvoice', blank=True, null=True)

    invoicings = GenericRelation(
        dd.plugins.invoicing.item_model,
        content_type_field='invoiceable_type',
        object_id_field='invoiceable_id')

    def get_invoicings(self, **kwargs):
        """Get a queryset with the invoicings which point to this enrolment.

        This is deprecated. Preferred way is to use
        :attr:`invoicings`.

        """
        item_model = dd.plugins.invoicing.item_model
        # item_model = rt.modules.sales.InvoiceItem
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
        """To be implemented by subclasses.  Return the product to put into
        the invoice item.

        """
        return None

    def get_invoiceable_qty(self):
        """To be implemented by subclasses.  Return the quantity to put into
        the invoice item.

        """
        return None

    def get_invoiceable_title(self, invoice=None):
        """Return the title to put into the invoice item.  May be overridden
        by subclasses.

        """
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
        """Yield a sequence of invoiceables (of this class) for the given
        plan.  If a `partner` is given, use it as an additional filter
        condition.

        """
        raise NotImplementedError()

    def setup_invoice_item(self, item):
        pass
