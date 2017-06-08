# Copyright 2008-2015 Luc Saffre
#
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
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('products.Products')
        m.add_action('products.ProductCats')

