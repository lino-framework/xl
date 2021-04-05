# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Adds functionality for handling incoming and outgoing invoices in a
VAT-less context (i.e. for organizations which have no obligation of
VAT declaration).  Site operators subject to VAT are likely to use
:mod:`lino_xl.lib.vat` instead.

Installing this plugin will automatically install
:mod:`lino_xl.lib.countries` and :mod:`lino_xl.lib.ledger`.


.. autosummary::
   :toctree:

    mixins

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    """See :class:`lino.core.plugin.Plugin`.

    """
    verbose_name = _("VAT-less invoicing")

    needs_plugins = ['lino_xl.lib.countries', 'lino_xl.lib.ledger']

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('vatless.Invoices')

