# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Adds functionality for managing meetings.

A **meeting** is a meeting between people where they discuss various tickets.

There is a configurable list of **wishes**. linking meetings to tickets.

The participants are **partnerlists**.

"""
# """
# .. autosummary::
#    :toctree:
#
#    models
#    choicelists
#    workflows
#    desktop
# """

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Meetings")

    needs_plugins = ['lino_xl.lib.cal']


    def setup_main_menu(self, site, profile, main):
        m = main.add_menu(self.app_label, self.verbose_name)
        m.add_action('meetings.MyMeetings')
        # m.add_separator()

    def setup_explorer_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('meetings.AllMeetings')
        
    def get_dashboard_items(self, user):
        for x in super(Plugin, self).get_dashboard_items(user):
            yield x
        if user.authenticated:
            yield self.site.actors.meetings.MyMeetings
            # yield self.site.actors.meetings.MyUpcommingMeetings