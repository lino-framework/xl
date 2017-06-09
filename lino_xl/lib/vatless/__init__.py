# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Luc Saffre
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


"""Adds functionality for handling incoming and outgoing invoices in a
VAT-less context (i.e. for organizations which have no obligation of
VAT declaration).  Site operators subject to VAT are likely to use
:mod:`lino_xl.lib.vat` instead.

Installing this plugin will automatically install
:mod:`lino_xl.lib.countries` and :mod:`lino_xl.lib.ledger`.


.. autosummary::
   :toctree:

    mixins
    models
    ui

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    """See :class:`lino.core.plugin.Plugin`.

    """
    verbose_name = _("VAT-less invoicing")

    needs_plugins = ['lino_xl.lib.countries', 'lino_xl.lib.ledger']

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('vatless.Invoices')

