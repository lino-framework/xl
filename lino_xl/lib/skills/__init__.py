# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""Adds the notions of "skills", including offers and demands thereof.

.. autosummary::
   :toctree:

   models
   desktop
   roles

"""

from lino.api import ad, _


class Plugin(ad.Plugin):

    verbose_name = _("Skills")

    needs_plugins = [
        # 'lino_noi.lib.noi',
        'lino_xl.lib.xl',
        # 'lino_xl.lib.tickets',
        'lino_noi.lib.contacts']

    # demander_model = 'tickets.Ticket'
    demander_model = 'contacts.Person'
    """
    The model of objects to be used as :attr:`demander
    <lino_xl.lib.skills.Demand.demander>` of skill
    demands. 
    """
    # demander_model = 'contacts.Partner'
    # demander_model = 'comments.Comment'
    # supplier_model = 'contacts.Person'
    # supplier_model = 'contacts.Partner'

    # end_user_model = 'users.User'
    end_user_model = 'contacts.Person'

    def on_site_startup(self, site):
        self.end_user_model = site.models.resolve(self.end_user_model)
        self.demander_model = site.models.resolve(self.demander_model)
        # self.supplier_model = site.models.resolve(self.supplier_model)
        super(Plugin, self).on_site_startup(site)
        
    def get_menu_group(self):
        return self
        # return self.site.plugins.get(
        #     self.demander_model._meta.app_label)
    
    def setup_main_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        # mg = site.plugins.tickets
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m.add_action('skills.Skills')
        # m.add_action('skills.Competences')
        m.add_action('skills.MyOffers')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('skills.TopLevelSkills')
        m.add_action('skills.AllSkills')
        m.add_action('skills.SkillTypes')

    def setup_explorer_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        # m.add_action('skills.Competences')
        m.add_action('skills.Offers')
        m.add_action('skills.Demands')

    def get_dashboard_items(self, user):
        for x in super(Plugin, self).get_dashboard_items(user):
            yield x
        if user.authenticated:
            if self.site.is_installed('tickets'):
                yield self.site.models.skills.SuggestedTicketsByEndUser
            yield self.site.models.skills.TopLevelSkills
                
