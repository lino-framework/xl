# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/coachings`.

.. autosummary::
   :toctree:

    desktop
    fixtures
    utils

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Coachings")

    needs_plugins = ['lino_xl.lib.contacts', 'lino_xl.lib.extensible']
    
    client_model = 'contacts.Person'

    def post_site_startup(self, site):
        self.client_model = site.models.resolve(self.client_model)
        super(Plugin, self).post_site_startup(site)

        site.kernel.memo_parser.register_django_model(
            'client', self.client_model,
            title=lambda obj: obj.get_full_name())
    
        
        
    # def setup_main_menu(self, site, user_type, m):
    #     mg = self.get_menu_group()
    #     m = m.add_menu(mg.app_label, mg.verbose_name)
    #     m.add_action('coachings.CoachedClients')
    #     m.add_action('coachings.MyCoachings')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('coachings.CoachingTypes')
        m.add_action('coachings.CoachingEndings')
        m.add_action('coachings.ClientContactTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('coachings.Coachings')
        m.add_action('coachings.ClientContacts')
        # m.add_action('coachings.ClientEvents')
        # m.add_action('coachings.ClientStates')
        

