# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds the concept of user groups.

See :doc:`/specs/groups`.
"""

from lino import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Groups")
    # member_model = 'users.User'
    menu_group = 'system'
    needs_plugins = ['lino.modlib.comments']

    # def on_plugins_loaded(self, site):
    #     site.plugins.comments.configure(
    #         commentable_model = 'groups.Group')

    # def on_site_startup(self, site):
    #     self.member_model = site.models.resolve(self.member_model)
    #     super(Plugin, self).on_site_startup(site)

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('groups.Groups')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('groups.AllMemberships')

    def get_dashboard_items(self, user):
        yield self.site.models.groups.MyGroups
