# Copyright 2008-2015 Luc Saffre
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

"""
Adds functionality for managing foos.

.. autosummary::
   :toctree:

    models
    fixtures.std
    fixtures.demo

"""

from lino import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Properties")

    def setup_explorer_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('properties.Properties')

    def setup_config_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('properties.PropGroups')
        m.add_action('properties.PropTypes')
        PropGroup = site.modules.properties.PropGroup
        PropsByGroup = site.modules.properties.PropsByGroup
        for pg in PropGroup.objects.all():
            m.add_action(
                PropsByGroup,
                params=dict(master_instance=pg),
                #~ label=pg.name)
                label=unicode(pg))
