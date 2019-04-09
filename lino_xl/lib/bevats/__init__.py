# Copyright 2008-2017 Rumma & Ko Ltd
"""Functionality for managing VAT declarations.

.. autosummary::
   :toctree:

    models
    desktop
    fixtures.std
    fixtures.payments

"""
# from importlib import import_module

from lino import ad


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    needs_plugins = ['lino_xl.lib.vat']

    # country_module = 'lino_xl.lib.declarations.be'
    # """select VAT declaration layout"""

    # def before_analyze(self):
    #     super(Plugin, self).before_analyze()
    #     import_module(self.country_module)
    
    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu("vat", site.plugins.vat.verbose_name)
        m.add_action('bevats.Declarations')
        m.add_action('bevats.DeclarationFields')


