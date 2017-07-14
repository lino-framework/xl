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

    def setup_explorer_menu(config, site, user_type, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        m.add_action('ana.Invoices')
        # m.add_action('ana.InvoiceItems')

