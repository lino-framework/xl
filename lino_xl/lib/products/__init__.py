# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds functionality for managing products.

.. autosummary::
   :toctree:

    fixtures.food
    fixtures.furniture

"""

from lino import ad, _


class Plugin(ad.Plugin):
    """The config descriptor for this plugin."""

    verbose_name = _("Products")
    needs_plugins = ['lino_xl.lib.xl']
    menu_group = 'products'

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        # if site.is_installed('sales'):
        #     mg = site.plugins.sales
        # else:
        #     mg = self
        m = m.add_menu(mg.app_label, mg.verbose_name)
        for pt in site.models.products.ProductTypes.get_list_items():
            m.add_action(pt.table_name, label=pt.text)
        # m.add_action('products.Products')
        m.add_action('products.ProductCats')

        # mg = site.plugins.sales
        # m2 = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('products.PriceRules')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('products.PriceFactors')

