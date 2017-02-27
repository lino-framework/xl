# Copyright 2014-2016 Luc Saffre
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


"""Adds functionality for handling sales.


.. autosummary::
    :toctree:

    models
    fixtures.std
    fixtures.demo_bookings

"""

from lino.api import ad
from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Product invoices")

    needs_plugins = ['lino_xl.lib.products', 'lino_xl.lib.vat']

    def setup_reports_menu(self, site, profile, m):
        mg = site.plugins.vat
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sales.DueInvoices')

    def setup_config_menu(self, site, profile, m):
        mg = site.plugins.vat
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sales.PaperTypes')

    def setup_explorer_menu(self, site, profile, m):
        mg = site.plugins.vat
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('sales.Invoices')
        m.add_action('sales.InvoiceItems')
