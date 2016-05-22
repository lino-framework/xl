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

from lino.api import dd, _
from lino.modlib.office.roles import OfficeStaff


class AddressType(dd.Choice):
    living_text = _("living at")


class AddressTypes(dd.ChoiceList):
    required_roles = dd.login_required(OfficeStaff)
    verbose_name = _("Address type")
    verbose_name_plural = _("Address types")
    item_class = AddressType

add = AddressTypes.add_item
add('01', _("Official address"), 'official')  # IT020
add('02', _("Unverified address"), 'unverified')  # IT042
add('03', _("Declared address"), 'declared')  # IT214
add('04', _("Reference address"), 'reference')
add('98', _("Obsolete"), 'obsolete')
add('99', _("Other"), 'other')


class DataSources(dd.ChoiceList):
    verbose_name = _("Data source")
    verbose_name_plural = _("Data sources")

add = DataSources.add_item
add('01', _("Manually entered"), 'manually')
add('02', _("Read from eID"), 'eid')


