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

"""Adds the notion of "user teams".

This is the base plugin which defines common things for all user teams:

- Define the `Team` model
- Inject into `users.User` a pointer to `teams.Team`
- Define a `UsersByTeam` view
- Add a menu command to configure the list of teams.


.. autosummary::
   :toctree:

    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("User teams")
    needs_plugins = ['lino.modlib.users']

    def setup_config_menu(config, site, profile, m):
        mg = site.plugins.system
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('teams.Teams')

