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


"""Adds a single VAT rule (:mod:`lino_xl.lib.vat.models.VatRule`)
which applies 0% for all
:attr:`lino_xl.lib.vat.choicelists.VatClasses`.  To be used by
organizations without VAT number but using :mod:`lino_xl.lib.vat`.

"""

from lino.api import rt


def objects():

    yield rt.models.vat.VatRule(rate=0)
