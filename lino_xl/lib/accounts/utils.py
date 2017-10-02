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
        if d is None: d = ZERO
        if c is None: c = ZERO
        if d > c:
            self.d = d - c
            self.c = ZERO
        else:
            self.c = c - d
            self.d = ZERO

    def __sub__(self, o):
        d1 = self.d or ZERO
        c1 = self.c or ZERO
        d2 = o.d or ZERO
        c2 = o.c or ZERO
        return Balance(d1-d2, c1-c2)
    
    def __add__(self, o):
        d1 = self.d or ZERO
        c1 = self.c or ZERO
        d2 = o.d or ZERO
        c2 = o.c or ZERO
        return Balance(d1+d2, c1+c2)
