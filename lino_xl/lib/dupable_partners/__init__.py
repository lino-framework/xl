# Copyright 2015 Luc Saffre
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

"""Adds functionality for avoiding duplicate partner records.

To use it, applications must do two things:

- add the following line to their :meth:`get_installed_apps
  <lino.core.site.Site.get_installed_apps>`::

    yield 'lino_xl.lib.dupable_partners'

- Override their :class:`contacts.Partner
  <lino.modlib.contacts.models.Partner>` model to inherit from
  :class:`lino_xl.lib.dupable_partners.mixins.DupablePartner`.

Defines a virtual slave table :class:`SimilarPartners`, which shows
the partners that are "similar" to a given master instance (and
therefore are potential duplicates).

See also :mod:`lino.mixins.dupable`.

A usage example is :mod:`lino.projects.min2`.
See also :mod:`lino_welfare.modlib.dupable_clients`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Dupable partners")

    needs_plugins = ['lino.modlib.contacts']

    def setup_explorer_menu(self, site, profile, main):
        mg = site.plugins.contacts
        m = main.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('dupable_partners.Words')
        
