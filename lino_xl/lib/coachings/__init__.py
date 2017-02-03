# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds the concept of coachings.

A **coaching** is when a given person (a client) is being coached by a
given user during a given period.

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

    needs_plugins = ['lino_xl.lib.contacts', 'lino_xl.lib.extensible']
    
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

