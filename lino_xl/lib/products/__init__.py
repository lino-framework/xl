# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds functionality for managing products.

.. autosummary::
   :toctree:

    models
    fixtures.food
    fixtures.furniture

"""

from lino import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Products")

    needs_plugins = ['lino_xl.lib.xl']

    def setup_main_menu(self, site, user_type, m):
        if site.is_installed('sales'):
            mg = site.plugins.sales
        else:
            mg = self
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('products.Products')
        m.add_action('products.ProductCats')

