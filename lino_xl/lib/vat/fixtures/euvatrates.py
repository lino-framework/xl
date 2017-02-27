# Copyright 2014-2016 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""Adds VAT rules (:mod:`lino_xl.lib.vat.models.VatRule`) for some
European countries.

"""

from lino.api import dd, rt


def objects():
    Country = rt.models.countries.Country
    # VatRule = rt.models.vat.VatRule
    vat = rt.models.vat

    def rule(vat_class, country_id, vat_regime, rate):
        if country_id is None:
            country = None
        else:
            try:
                country = Country.objects.get(pk=country_id)
            except Country.DoesNotExist:
                raise Exception("No country {0}".format(country_id))
        return vat.VatRule(
            country=country,
            vat_class=vat.VatClasses.get_by_name(vat_class),
            # trade_type=vat.TradeTypes.get_by_name(trade_type),
            vat_regime=vat.VatRegimes.get_by_name(vat_regime),
            rate=rate)

    yield rule('exempt', None, None, 0)

    yield rule('normal', 'BE', None, '0.21')
    yield rule('reduced', 'BE', None, '0.07')

    yield rule('normal', 'EE', None, '0.20')
    yield rule('reduced', 'EE', None, '0.09')

    yield rule('normal', 'NL', None, '0.21')
    yield rule('reduced', 'NL', None, '0.06')

    yield rule('normal', 'DE', None, '0.19')
    yield rule('reduced', 'DE', None, '0.07')

    yield rule('normal', 'FR', None, '0.20')
    yield rule('reduced', 'FR', None, '0.10')
    # in FR there are more VAT classes, we currently don't support them
    # yield rule('reduced', 'FR', None, None, '0.055')
    # yield rule('reduced', 'FR', None, None, '0.021')

