# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/ana`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Analytical accounting")
    needs_plugins = ['lino_xl.lib.ledger']

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('ana.Groups')
        m.add_action('ana.Accounts')

    def setup_reports_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        # mg = site.plugins.vat
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ana.PrintableInvoicesByJournal')
        m.add_action('ana.AnalyticAccountBalances')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        # mg = site.plugins.vat
        # mg = self
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ana.Invoices')
        # m.add_action('ana.InvoiceItems')

