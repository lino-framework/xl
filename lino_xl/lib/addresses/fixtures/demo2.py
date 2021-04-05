# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Adds some additional non-primary addresses to some partners.

"""

from lino.api import dd, rt

from lino.utils import Cycler
from lino.utils.demonames.bel import streets_of_eupen


def objects():
    AddressTypes = rt.models.addresses.AddressTypes
    Address = rt.models.addresses.Address
    # Partner = rt.models.contacts.Partner
    Partner = dd.plugins.addresses.partner_model
    Place = rt.models.countries.Place
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
