# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.ad import Plugin, _


class Plugin(Plugin):

    verbose_name = _("Blog")

    needs_plugins = ['lino_xl.lib.topics']

    def setup_main_menu(self, site, user_type, m):
        # mg = self.get_menu_group()
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.MyEntries')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.EntryTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.AllEntries')
        # m.add_action('blogs.AllTaggings')

    def get_quicklinks(self, user):
        yield dict(instance=user,
            action=self.site.models.blogs.MyEntries.insert_action,
            label=_("New blog entry"))


    # def get_dashboard_items(self, user):
    #     from lino.core.dashboard import ActorItem
    #     yield ActorItem(
    #         self.site.models.blogs.LatestEntries, header_level=None)
        # yield CustomItem(
        #     'blogs.Entry.latest_entries',
        #     self.models.blogs.Entry.latest_entries, max_num=10)
