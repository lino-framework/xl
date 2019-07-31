# -*- coding: UTF-8 -*-
# Copyright 2016-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Sets `payment_term` of all partners.

"""

from lino.utils import Cycler
from lino.api import dd, rt, _


def objects():

    PaymentTerm = rt.models.ledger.PaymentTerm
    Worker = dd.plugins.ledger.worker_model
    if Worker is not None:
        kwargs = {}
        kwargs['worker'] = Worker.objects.get(first_name="Robin")
        kwargs['ref'] = "robin"
        kwargs = dd.str2kw('name', _("Cash Robin"), **kwargs)
        yield PaymentTerm(**kwargs)

    PAYMENT_TERMS = Cycler(PaymentTerm.objects.all())

    for obj in rt.models.contacts.Partner.objects.all():
        obj.payment_term = PAYMENT_TERMS.pop()
        yield obj
