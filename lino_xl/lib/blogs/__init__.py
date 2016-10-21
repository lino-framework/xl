# -*- coding: UTF-8 -*-
# Copyright 2013-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

from lino.ad import Plugin
from django.utils.translation import ugettext_lazy as _


class Plugin(Plugin):

    verbose_name = _("Blog")
    
    needs_plugins = ['lino_xl.lib.topics']


    def setup_main_menu(self, site, profile, m):
        # mg = self.get_menu_group()
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.MyEntries')

    def setup_config_menu(self, site, profile, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.EntryTypes')

    def setup_explorer_menu(self, site, profile, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('blogs.AllEntries')
        m.add_action('blogs.AllTaggings')
