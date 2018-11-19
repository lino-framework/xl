# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Specify a healthcare plan on your clients and issue cost-sharing
invoices to their healthcare providers.

The **client fee** of a plan is what the client pays out of pocket

See :doc:`/specs/healthcare`.

.. autosummary::
   :toctree:

    fixtures.demo
"""

from lino.api import ad, _


class Plugin(ad.Plugin):

    verbose_name = _("Healthcare")
    menu_group = "contacts"

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('healthcare.Plans')
        
    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('healthcare.Rules')
