# Copyright 2008-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Adds functionality for linking Github repos's commits to tickets via user Sessions.

.. autosummary::
   :toctree:

    models
"""

import six

from lino.api import ad, _
import re

class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    # verbose_name = _("Clocking")
    verbose_name = _("GitHub")

    needs_plugins = ['lino_xl.lib.working',
                     'lino_xl.lib.tickets',
                     ]

    ticket_pattern = re.compile(r"(?<!Merge pull request )#([0-9]+)")

    def on_site_startup(self, site):
        # from .mixins import Workable
        pass

    def setup_main_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('github.MyCommits')
        # m.add_action('github.MyUnasignedCommits')
        # m.add_action('github.UnknownUserCommits')

    def setup_config_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('github.Repositories')

    def setup_explorer_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('github.Commits')

        # def get_dashboard_items(self, user):
        #     if user.authenticated:
