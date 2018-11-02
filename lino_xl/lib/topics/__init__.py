# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds the concepts of "topics" and "interests".  See
:doc:`/specs/topics`.


.. autosummary::
   :toctree:

    roles

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    """
    A subclass of :class:`Plugin <lino.core.plugin.Plugin>` for this
    plugin.
    """

    verbose_name = _("Topics")
    
    needs_plugins = ['lino_xl.lib.xl', 'lino.modlib.gfks']

    # partner_model = 'users.User'
    partner_model = 'contacts.Partner'
    """
    The Django model used to represent partners in the scope of this
    plugin.
    """
    
    # menu_group = 'contacts'

    def setup_config_menu(self, site, user_type, m):
        p = self.get_menu_group()
        # p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.AllTopics')
        # m.add_action('topics.TopicGroups')

    def setup_explorer_menu(self, site, user_type, m):
        p = self.get_menu_group()
        # p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.AllInterests')
