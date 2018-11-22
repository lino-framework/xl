# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Implements functionality for getting statistics about users.  See
:doc:`/specs/userstats`.

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("User Statistics")

    needs_plugins = ['lino.modlib.users']

    def setup_explorer_menu(self, site, user_type, m):
        g = site.plugins.system
        m = m.add_menu(g.app_label, g.verbose_name)
        m.add_action('userstats.UserStats')

