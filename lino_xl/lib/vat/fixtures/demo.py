# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


import random
from lino.utils import Cycler
from lino.api import rt
from lino_xl.lib.vat.choicelists import VatAreas, VatRegimes, VatRules

# Thanks to https://www.avalara.com/vatlive/en/eu-vat-rules/eu-vat-number-registration/eu-vat-number-formats.html
vat_id_lengths = {
    "AT": 8,
    "BE": 10,
    "HR": 11,
    "DK": 8,
    "EE": 10,
    "FI": 8,
    "FR": 11,
    "DE": 9,
    "NL": 9,
    "EL": 9,
    "HU": 8,
    "IT": 11,
    "LV": 11,
    "LT": 12,
    "LU": 8,
 }


def objects():
    random.seed(1)  # we want always the same sequence of random numbers
    qs = rt.models.contacts.Company.objects.filter(country__isnull=False)
    qs = qs.filter(vat_id="")
    for obj in qs:
        isocode = obj.country.isocode
        length = vat_id_lengths.get(isocode, None)
        if not length:
            # raise Exception("20190408 no VAT id length for {}".format(isocode))
            continue
        number = str(random.randint(int("1" * length), int("9" * length)))
        if isocode == "AT":
            number = "U" + number
        elif isocode == "NL":
            number = number + "B01"
        obj.vat_id = "{}{}".format(isocode, number)
        yield obj

    va2regimes = dict()
    for va in VatAreas.get_list_items():
        regimes = []
        for reg in VatRegimes.get_list_items():
            if reg.is_allowed_for(va) and reg.name not in ('lu', 'de'):
                # if va.name == "national":
                #     raise Exception("20190408 ok")
                if VatRules.get_vat_rule(
                        va, vat_regime=reg, default=False):
                    regimes.append(reg)
        if len(regimes) == 0:
            raise Exception("20190408 no regimes for {}".format(va))
        va2regimes[va] = Cycler(regimes)

    if len(va2regimes) == 0:
        msg = "No VAT rules defined. "
        msg += "The VAT plugin requires a declaration plugin xxvat"
        raise Exception(msg)

    qs = rt.models.contacts.Partner.objects.filter(country__isnull=False)
    qs = qs.filter(vat_regime="")
    for obj in qs:
        va = VatAreas.get_for_country(obj.country)
        if va is None:
            raise Exception("20190408 no VAT area for {}".format(obj.country))
        regs = va2regimes.get(va)
        regs = list(regs.items)
        reg = regs.pop(0)
        if obj.vat_id:
            # prefer a reg that needs vat id
            while len(regs) and not reg.needs_vat_id:
                reg = regs.pop(0)
                # print("20200121a", reg, regs)
        else:
            while len(regs) and reg.needs_vat_id:
                reg = regs.pop(0)
                # print("20200121b", reg, regs)
        obj.vat_regime = reg
        yield obj
        # else:
        #     raise Exception("20190408 no VAT regime for {}".format(obj))
