# -*- coding: UTF-8 -*-
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

"""Choicelists for :mod:`lino_xl.lib.notes`.

.. autosummary::

"""

from lino.api import dd, rt, _


class SpecialType(dd.Choice):
    """Represents a special note type."""

    def get_notes(self, **kw):
        """Return a queryset with the uploads of this shortcut."""
        return rt.modules.notes.Note.objects.filter(
            type__special_type=self, **kw)


class SpecialTypes(dd.ChoiceList):
    """The list of special note types which have been declared on this
    Site.

    """
    verbose_name = _("Special note type")
    verbose_name_plural = _("Special note types")
    item_class = SpecialType
    max_length = 5
