# Copyright 2008-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""
Adds functionality for managing "milestones" and "deployments".

See :doc:`/specs/noi/deploy`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Deploy")

    needs_plugins = ['lino_xl.lib.tickets']

    # def setup_main_menu(self, site, user_type, m):
    #     # p = self.get_menu_group()
    #     p = site.plugins.tickets
    #     m = m.add_menu(p.app_label, p.verbose_name)
    #     m.add_action('deploy.MyMilestones')

    # def setup_config_menu(self, site, user_type, m):
    #     p = self.get_menu_group()
    #     m = m.add_menu(p.app_label, p.verbose_name)
    #     # m.add_action('tickets.Projects')

    def setup_explorer_menu(self, site, user_type, m):
        # p = self.get_menu_group()
        p = site.plugins.tickets
        m = m.add_menu(p.app_label, p.verbose_name)
        # m.add_action('deploy.Milestones')
        m.add_action('deploy.Deployments')
        
    # def get_dashboard_items(self, user):
    #     if user.authenticated:
    #         yield self.site.models.deploy.MyMilestones
