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

"""See :mod:`ml.boards`.

.. autosummary::
   :toctree:

    models
    mixins

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Boards")

    def setup_config_menu(config, site, profile, m):
        menu_host = site.plugins.contacts
        m = m.add_menu(menu_host.app_label, menu_host.verbose_name)
        m.add_action('boards.Boards')

    def setup_explorer_menu(config, site, profile, m):
        menu_host = site.plugins.contacts
        m = m.add_menu(menu_host.app_label, menu_host.verbose_name)
        m.add_action('boards.Members')

