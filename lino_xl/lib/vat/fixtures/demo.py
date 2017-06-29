# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Sets `vat_regime` of all partners.

"""


from lino.utils import Cycler
from lino.api import rt


def objects():

    REGIMES = Cycler(rt.models.vat.VatRegimes.get_list_items())

    for obj in rt.models.contacts.Partner.objects.all():
        obj.vat_regime = REGIMES.pop()
        yield obj
