# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.


"""Adds the concepts of "topics" and "interests".

.. autosummary::
   :toctree:

    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Topics")

    needs_plugins = ['lino.modlib.contacts']

    # def setup_main_menu(self, site, profile, m):
    #     # p = self.get_menu_group()
    #     p = self.site.plugins.contacts
    #     m = m.add_menu(p.app_label, p.verbose_name)

    def setup_config_menu(self, site, profile, m):
        # p = self.get_menu_group()
        p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.Topics')
        m.add_action('topics.TopicGroups')

    def setup_explorer_menu(self, site, profile, m):
        # p = self.get_menu_group()
        p = self.site.plugins.contacts
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('topics.Interests')
