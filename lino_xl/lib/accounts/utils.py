# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from decimal import Decimal
from lino.api import _

ZERO = Decimal(0)

DEBIT = True
CREDIT = False

DCLABELS = {
    DEBIT: _("Debit"),
    CREDIT: _("Credit")
}

class Balance(object):
    def __init__(self, d, c):
        if d > c:
            self.d = d - c
            self.c = ZERO
        else:
            self.c = c - d
            self.d = ZERO


