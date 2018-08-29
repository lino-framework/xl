# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Sets `payment_term` of all partners.

"""

from lino.utils import Cycler
from lino.api import rt


def objects():

    PAYMENT_TERMS = Cycler(rt.models.ledger.PaymentTerm.objects.all())

    for obj in rt.models.contacts.Partner.objects.all():
        obj.payment_term = PAYMENT_TERMS.pop()
        yield obj
        
