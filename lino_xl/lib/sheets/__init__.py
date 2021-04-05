# -*- coding: UTF-8 -*-
# Copyright 2018-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Add functionality for producing accounting statements that work using "sheet
items".  In practice this means the *Balance sheet* and the *Income statement*.

See :doc:`/specs/sheets`.
"""

import locale

from lino.api import ad, _

class Plugin(ad.Plugin):
    verbose_name = _("Accounting report")
    # needs_plugins = ['lino_xl.lib.ledger', 'lino.modlib.summaries']
    needs_plugins = ['lino_xl.lib.ledger']

    item_ref_width = 4
    """
    The display width of the :guilabel:`Reference` field of a sheet
    item.
    """

    def on_init(self):
        super(Plugin, self).on_init()
        if self.site.site_locale is None:
            self.site.site_locale = '.'.join(locale.getdefaultlocale())

    def setup_reports_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sheets.Report', action='start_plan')

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sheets.Items')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sheets.Reports')
        m.add_action('sheets.CommonItems')
        m.add_action('sheets.AccountEntries')
        m.add_action('sheets.AnaAccountEntries')
        m.add_action('sheets.PartnerEntries')
        m.add_action('sheets.ItemEntries')
        # m.add_action('sheets.ItemEntries')
        # m.add_action('sheets.AnaAcountEntries')
