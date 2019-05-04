# Copyright 2018-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Manage a list of health care plans and their providers, and assign them to your
clients.

See :doc:`/specs/healthcare`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):

    verbose_name = _("Healthcare")
    menu_group = "contacts"

    client_model = 'contacts.Person'
    """The model used as "client" in your application. """

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('healthcare.Plans')
        m.add_action('healthcare.Rules')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('healthcare.Tariffs')
        m.add_action('healthcare.Situations')
