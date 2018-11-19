# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Utilities for this plugin.


"""

from decimal import Decimal, ROUND_HALF_UP
from lino.api import _

ZERO = Decimal(0)
CENT = Decimal('.01')
HUNDRED = Decimal('100.00')
ONE = Decimal('1.00')
MAX_AMOUNT = Decimal("9999999.00")

DEBIT = False
CREDIT = True

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

    def __str__(self):
        if self.d:
            return "{} DB".format(self.d)
        return "{} CR".format(self.c)
    
    def __repr__(self):
        return "Balance({},{})".format(self.d, self.c)
        return "{} CR".format(self.c)
    
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

    def value(self, dc):
        if dc is DEBIT:
            return self.d - self.c
        else:
            return self.c - self.d
    

def myround(d):
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


