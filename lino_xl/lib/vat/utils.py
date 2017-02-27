# -*- coding: UTF-8 -*-
# Copyright 2008-2015 Luc Saffre
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


"""Utility function for `lino_xl.lib.vat`.

>>> from decimal import Decimal
>>> from lino_xl.lib.vat.utils import add_vat, remove_vat
>>> rate = Decimal(21)
>>> add_vat(100, rate)
Decimal('121')
>>> remove_vat(Decimal('121.00'), rate)
Decimal('100')

"""

from __future__ import unicode_literals

from decimal import Decimal
from lino_xl.lib.accounts.utils import ZERO

HUNDRED = Decimal('100')
# ZERO = Decimal('0.00')
ONE = Decimal('1.00')


def add_vat(base, rate):
    "Add to the given base amount `base` the VAT of rate `rate`."
    return base * (HUNDRED + rate) / HUNDRED


def remove_vat(incl, rate):
    "Remove from the given amount `incl` the VAT of rate `rate`."
    return incl / ((HUNDRED + rate) / HUNDRED)
