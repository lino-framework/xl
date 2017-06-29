# Copyright 2008-2017 Luc Saffre
"""Functionality for managing VAT declarations.

.. autosummary::
   :toctree:

    choicelists
    be
    models
    desktop
    fixtures.demo_bookings

"""

from lino import ad


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    country_module = 'lino_xl.lib.declarations.be'
    
    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu("vat", site.plugins.vat.verbose_name)
        m.add_action('declarations.Declarations')


