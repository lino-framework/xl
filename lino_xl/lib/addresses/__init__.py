# Copyright 2014-2015 Luc Saffre
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

"""Adds functionality and models to handle multiple addresses per
:class:`lino_xl.lib.contacts.models.Partner`. When this module is
installed, your application usually has a "Manage addresses" button
per partner.

.. autosummary::
   :toctree:

    choicelists
    mixins
    models
    fixtures.demo2

Some unit test cases are :mod:`lino.projects.min2.tests.test_addresses`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."
    verbose_name = _("Addresses")

    def setup_explorer_menu(self, site, profile, m):
        # mg = self.get_menu_group()
        mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('addresses.AddressTypes')
        m.add_action('addresses.Addresses')

