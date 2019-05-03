# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str

from lino.utils.instantiator import Instantiator
from lino.api import rt


Company = rt.models.contacts.Company
# Plan = rt.models.healthcare.Plan

def provider(name, country, plans=""):
    return Company(name=name, country_id=country)
    # yield prov
    # yield Plan(provider=prov)
    # for ref in plans.split():
    #     yield Plan(provider=prov, ref=ref)

def objects():

    yield provider("Eesti Haigekassa", "EE")
    yield provider("Mutualité Chrétienne", "BE", "vipo")
    yield provider("Solidaris", "BE")

