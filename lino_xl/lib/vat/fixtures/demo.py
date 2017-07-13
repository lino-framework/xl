# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Sets `vat_regime` of all partners.

"""


from lino.utils import Cycler
from lino.api import rt


def objects():
    TradeTypes = rt.models.ledger.TradeTypes
    VatRule = rt.models.vat.VatRule
    VatRegimes = rt.models.vat.VatRegimes
    
    regimes = []
    for tt in TradeTypes.get_list_items():
        for reg in VatRegimes.get_list_items():
            if VatRule.get_vat_rule(tt, reg, default=False):
                regimes.append(reg)

    if len(regimes) == 0:
        raise Exception("No VAT regimes! Please load either novat or euvatrates before demo!")

    REGIMES = Cycler(regimes)

    for obj in rt.models.contacts.Partner.objects.all():
        obj.vat_regime = REGIMES.pop()
        yield obj
