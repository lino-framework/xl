# -*- coding: UTF-8 -*-
# Copyright 2008-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Utility functions for VAT.

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


