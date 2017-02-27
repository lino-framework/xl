# -*- coding: UTF-8 -*-
# Copyright 2012-2015 Luc Saffre
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


r"""Utilities for `lino_xl.lib.accounts`.


"""

from decimal import Decimal
from lino.api import _

ZERO = Decimal(0)

DEBIT = True
CREDIT = False

DCLABELS = {
    DEBIT: _("Debit"),
    CREDIT: _("Credit")
}

