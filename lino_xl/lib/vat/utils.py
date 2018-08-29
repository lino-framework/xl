# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Utility functions for VAT.

.. $ python setup.py test -s tests.LibTests.test_vat_utils

>>> from lino_xl.lib.vat.utils import add_vat, remove_vat

>>> add_vat(100, 21)
121.0

>>> remove_vat(121, 21)
100.0

>>> add_vat(10, 21)
12.1

>>> add_vat(1, 21)
1.21

"""

from __future__ import division
from __future__ import unicode_literals

def add_vat(base, rate):
    "Add to the given base amount `base` the VAT of rate `rate`."
    # return base * (HUNDRED + rate) / HUNDRED
    return base * (100 + rate) / 100


def remove_vat(incl, rate):
    "Remove from the given amount `incl` the VAT of rate `rate`."
    # return incl / ((HUNDRED + rate) / HUNDRED)
    return incl / ((100 + rate) / 100)
