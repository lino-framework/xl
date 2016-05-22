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
"""Adds some additional non-primary addresses to some partners.

"""

from lino.api import rt

from lino.utils import Cycler
from lino.utils.demonames.bel import streets_of_eupen


def objects():
    AddressTypes = rt.modules.addresses.AddressTypes
    Address = rt.modules.addresses.Address
    Partner = rt.modules.contacts.Partner
    Place = rt.modules.countries.Place
    eupen = Place.objects.get(name__exact='Eupen')
    STREETS = Cycler(streets_of_eupen())
    TYPES = Cycler(AddressTypes.objects())

    def create_addr_from_owner(o, **kw):
        kw.update(partner=o)
        for k in Address.ADDRESS_FIELDS:
            kw[k] = getattr(o, k)
        return Address(**kw)

    nr = 1
    for p in Partner.objects.filter(city=eupen):
        if nr % 3:
            yield create_addr_from_owner(
                p, primary=True, address_type=AddressTypes.official)
            kw = dict(partner=p)
            kw.update(address_type=TYPES.pop())
            kw.update(street=STREETS.pop())
            kw.update(street_no=str(nr % 200))
            yield Address(**kw)
        nr += 1
