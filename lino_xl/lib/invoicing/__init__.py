# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
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


"""Adds functionality and database models for **invoicing**,
i.e. automatically generating invoices from data in the database.

See :doc:`/specs/cosi/invoicing` for a functional specification.

.. autosummary::
    :toctree:

    models
    mixins
    actions
    fixtures.demo_bookings

"""

from lino.api.ad import Plugin, _


class Plugin(Plugin):
    """

    .. attribute:: voucher_model

    """

    # needs_plugins = ['lino_xl.lib.ledger']
    needs_plugins = ['lino_xl.lib.sales']

    voucher_model = 'sales.VatProductInvoice'
    item_model = 'sales.InvoiceItem'
    """The database model into which invoiceable objects should create
    invoice items.  Default value refers to
    :class:`sales.InvoiceItem <lino_xl.lib.sales.models.InvoiceItem>`.

    This model will have an injected GFK field `invoiceable`.

    """

    invoiceable_label = _("Invoiced object")

    def on_site_startup(self, site):
        from lino.core.utils import resolve_model
        self.voucher_model = resolve_model(self.voucher_model)
        self.item_model = resolve_model(self.item_model)
        
    def get_voucher_type(self):
        # from lino.core.utils import resolve_model
        # model = resolve_model(self.voucher_model)
        # return self.site.modules.ledger.VoucherTypes.get_for_model(model)
        return self.site.modules.ledger.VoucherTypes.get_for_model(
            self.voucher_model)

    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m.add_action('invoicing.MyPlans')
        m.add_action('invoicing.Plan', action='start_invoicing')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.vat
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('invoicing.AllPlans')
