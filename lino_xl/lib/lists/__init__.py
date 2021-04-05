# Copyright 2014-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Adds the concept of partner lists.
"""

from lino import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."
    verbose_name = _("Lists")
    partner_model = 'contacts.Partner'
    menu_group = 'contacts'

    def on_site_startup(self, site):
        self.partner_model = site.models.resolve(self.partner_model)
        super(Plugin, self).on_site_startup(site)

    def setup_main_menu(self, site, user_type, m):
        # mg = site.plugins.contacts
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('lists.Lists')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        # mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('lists.ListTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        # mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('lists.AllMembers')
