# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Sets `vat_regime` of all partners.

"""


from lino.utils import Cycler
from lino.api import rt
from lino_xl.lib.vat.choicelists import VatAreas, VatRegimes


def objects():
    # TradeTypes = rt.models.ledger.TradeTypes
    VatRule = rt.models.vat.VatRule
    # VatRegimes = rt.models.vat.VatRegimes
    
    va2regimes = dict()
    for va in VatAreas.get_list_items():
        regimes = []
        for reg in VatRegimes.get_list_items():
            if reg.is_allowed_for(va):
                if VatRule.get_vat_rule(va, vat_regime=reg, default=False):
                    regimes.append(reg)
                
        # for reg in VatRegimes.get_list_items():
        #     for tt in TradeTypes.get_list_items():
        #         if reg not in nat_regimes:
        #             vr = VatRule.get_vat_rule(
        #                 tt, reg, country=my_country, default=False)
        #             if vr:
        #                 nat_regimes.append(reg)
        #         if reg not in int_regimes:
        #             vr = VatRule.get_vat_rule(tt, reg, default=False)
        #             if vr:
        #                 int_regimes.append(reg)
        va2regimes[va] = Cycler(regimes)

    # if len(nat_regimes) == 0 or len(int_regimes) == 0:
    if len(va2regimes) == 0:
        msg = "No vat rules defined. "
        # msg = "{} national and ".format(len(nat_regimes))
        # msg += "{} international regimes. ".format(len(int_regimes))
        msg += "Please load either novat or euvatrates before demo! "
        # msg += "Your plugins.countries.country_code is {}. ".format(
        #     my_country.isocode)
        # regimes = VatRegimes.get_list_items()
        raise Exception(msg)

    # NAT_REGIMES = Cycler(nat_regimes)
    # INT_REGIMES = Cycler(int_regimes)

    for obj in rt.models.contacts.Partner.objects.filter(
            country__isnull=False):
        va = VatAreas.get_for_country(obj.country)
        regs = va2regimes.get(va)
        obj.vat_regime = regs.pop()
        # if obj.country == my_country:
        #     obj.vat_regime = NAT_REGIMES.pop()
        # else:
        #     obj.vat_regime = INT_REGIMES.pop()
        yield obj
