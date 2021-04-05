# -*- coding: UTF-8 -*-
# Copyright 2008-2016 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Adds functionality for "starring" database objects (marking them as
"favourite").

Note that this plugin is maybe going to replaced by a
yet-to-be-written :mod:`lino_xl.lib.votes` plugin (:ticket:`831`). The
biggest difference being that the latter does not use a GFK and
therefore is more extendable.


.. autosummary::
   :toctree:

    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Stars")

    needs_plugins = ['lino.modlib.changes', 'lino.modlib.office']

    def setup_main_menu(self, site, user_type, m):
        # p = self.get_menu_group()
        p = self.site.plugins.office
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('stars.MyStars')

    def setup_explorer_menu(self, site, user_type, m):
        # p = self.get_menu_group()
        p = self.site.plugins.office
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('stars.AllStars')
