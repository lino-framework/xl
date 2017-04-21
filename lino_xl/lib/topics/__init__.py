# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


"""Adds the concepts of "topics" and "interests".

This plugin suggests but does not require :mod:`lino_xl.lib.contacts`.


.. autosummary::
   :toctree:

    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Topics")
    
    needs_plugins = ['lino_xl.lib.xl']
    # needs_plugins = ['lino_xl.lib.contacts']

    partner_model = 'contacts.Partner'
    menu_group = 'contacts'
    # partner_model = 'users.User'

    # def setup_main_menu(self, site, profile, m):
    #     # p = self.get_menu_group()
    #     p = self.site.plugins.contacts
    #     m = m.add_menu(p.app_label, p.verbose_name)

    def setup_config_menu(self, site, profile, m):
        p = self.get_menu_group()
        # p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.AllTopics')
        m.add_action('topics.TopicGroups')

    def setup_explorer_menu(self, site, profile, m):
        p = self.get_menu_group()
        # p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.AllInterests')
