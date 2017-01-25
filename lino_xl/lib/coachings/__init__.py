# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""

The :mod:`lino_welfare.modlib.pcsw` package provides data definitions
for PCSW specific objects.

.. autosummary::
   :toctree:

    roles
    mixins
    choicelists
    models
    desktop
    fixtures
    utils


"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Coachings")

    needs_plugins = ['lino_xl.lib.contacts']
    
    client_model = 'contacts.Person'

    def on_site_startup(self, site):
        self.client_model = site.models.resolve(self.client_model)
        super(Plugin, self).on_site_startup(site)
        
    # def setup_main_menu(self, site, profile, m):
    #     mg = self.get_menu_group()
    #     m = m.add_menu(mg.app_label, mg.verbose_name)
    #     m.add_action('coachings.CoachedClients')
    #     m.add_action('coachings.MyCoachings')

    def setup_config_menu(self, site, profile, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('coachings.CoachingTypes')
        m.add_action('coachings.CoachingEndings')
        m.add_action('coachings.ClientContactTypes')

    def setup_explorer_menu(self, site, profile, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('coachings.Coachings')
        m.add_action('coachings.ClientContacts')

