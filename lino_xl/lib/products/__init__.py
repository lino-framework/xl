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
    "See :class:`lino.core.Plugin`."

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
            m.add_action(pt.table_name)
        # m.add_action('products.Products')
        m.add_action('products.ProductCats')

