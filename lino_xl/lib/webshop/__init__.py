# Copyright 2021 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Adds functionality for webshops.

See :doc:`/specs/webshop`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Webshop")
    needs_plugins = ['lino_xl.lib.contacts', 'lino_xl.lib.sales']
    # menu_group = 'sales'

    journal_ref = "SLS"
    """The reference of the journal"""

    def get_quicklinks(site, user):
        yield 'products.Products'
        yield 'webshop.MyCart.start_plan'  # returns the wrong bound action.

    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.sales
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('webshop.MyAddresses')
        m.add_action('webshop.MyCart.start_plan')

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('webshop.PaymentMethods')
        m.add_action('webshop.DeliveryMethods')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('webshop.AllCarts')
        m.add_action('webshop.AllAddresses')
