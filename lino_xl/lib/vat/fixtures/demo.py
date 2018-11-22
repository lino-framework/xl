# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Sets `vat_regime` of all partners.

"""


from lino.utils import Cycler
from lino.api import rt
from lino_xl.lib.vat.choicelists import VatAreas, VatRegimes, VatRules


def objects():
    va2regimes = dict()
    for va in VatAreas.get_list_items():
        regimes = []
        for reg in VatRegimes.get_list_items():
            if reg.is_allowed_for(va):
                if VatRules.get_vat_rule(
                        va, vat_regime=reg, default=False):
                    regimes.append(reg)
                
        va2regimes[va] = Cycler(regimes)

    if len(va2regimes) == 0:
        msg = "No vat rules defined. "
        # msg += "Please load either novat or euvatrates before demo! "
        msg += "vat plugin requires an implementor plugin xxvat"
        raise Exception(msg)

    for obj in rt.models.contacts.Partner.objects.filter(
            country__isnull=False):
        va = VatAreas.get_for_country(obj.country)
        regs = va2regimes.get(va)
        obj.vat_regime = regs.pop()
        yield obj
