# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/clients`.

.. autosummary::
   :toctree:

    desktop

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Clients")
    needs_plugins = ['lino_xl.lib.contacts']
    
    client_model = 'contacts.Person'
    """The model to which :attr:`ClientContact.client` points to."""

    def post_site_startup(self, site):
        self.client_model = site.models.resolve(self.client_model)
        super(Plugin, self).post_site_startup(site)
        rdm = site.kernel.memo_parser.register_django_model
        rdm('client', self.client_model,
            title=lambda obj: obj.get_full_name())
        
    # def setup_main_menu(self, site, user_type, m):
    #     mg = self.get_menu_group()
    #     m = m.add_menu(mg.app_label, mg.verbose_name)
    #     m.add_action('coachings.CoachedClients')
    #     m.add_action('coachings.MyCoachings')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('clients.ClientContactTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('clients.ClientContacts')
        m.add_action('clients.KnownContactTypes')
        

