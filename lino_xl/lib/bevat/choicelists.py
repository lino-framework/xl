# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Declaration fields.
"""

from __future__ import unicode_literals

# from django.db import models
# from django.conf import settings
#from django.utils.translation import string_concat
from lino_xl.lib.accounts.utils import DEBIT, CREDIT

from lino.api import dd, rt, _

from lino_xl.lib.vat.choicelists import DeclarationFieldsBase


class DeclarationFields(DeclarationFieldsBase):
    pass

# afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field

# (II) sales base 
mfld("00", DEBIT, '00', _("Sales 0%"))
mfld("01", DEBIT, '01', _("Sales 6%"))
mfld("02", DEBIT, '02', _("Sales 12%"))
mfld("03", DEBIT, '03', _("Sales 20%"))
mfld("44", DEBIT, "00 01 02 03", _("Sales located inside EU"),
      vat_regimes="inside")
mfld("45", DEBIT, "00 01 02 03",  _("Sales to co-contractors"),
      vat_regimes="cocontractor")
mfld("46", DEBIT, "00 01 02 03", _("Sales intracom and ABC"),
      vat_regimes="intracom")
mfld("47", DEBIT, "00 01 02 03", _("Sales 47"),
      vat_regimes="intracom")
mfld("48", CREDIT, "00 01 02 03", _("CN sales 48"))
mfld("49", CREDIT, "00 01 02 03", _("CN sales 49"))

# (III) purchases base

mfld("81", CREDIT, '81', _("Ware"))
mfld("82", CREDIT, '82', _("Services"))
mfld("83", CREDIT, '83', _("Investments"))

mfld("84", DEBIT, "81 82 83", 
      _("CN purchases on operations in 86 and 88"),
      vat_regimes="intracom", only_dc=True)
mfld("85", DEBIT, "81 82 83", _("CN purchases on other operations"),
      vat_regimes="!intracom !delayed")
mfld("86", CREDIT, "81 82 83",
      _("IC purchases and ABC sales"), 
      vat_regimes="intracom")
mfld("87", CREDIT, "81 82 83", _("Other purchases in Belgium"),
      vat_regimes="cocontractor")
mfld("88", CREDIT, "81 82 83", _("IC services"),
      vat_regimes="delayed")

# (IV) DUE TAXES

mfld("54", DEBIT, '54', _("Due VAT for 01, 02 and 03"),
     vat_regimes="!intracom !delayed !cocontractor", is_payable=True)
mfld("55", DEBIT, '54', _("Due VAT for 86 and 88"),
     vat_regimes="intracom", is_payable=True)
mfld("56", DEBIT, '54',
      _("Due VAT for 87 except those covered by 57"),
     vat_regimes="cocontractor", is_payable=True)
mfld("57", DEBIT, '54',
      _("Due VAT for 87 except those covered by 57"),
      vat_regimes="delayed", is_payable=True)
wfld("61", DEBIT, None, _("Miscellaneous corrections due"),
     is_payable=True)

sfld("XX", DEBIT, None, _("Total of due taxes"),
     "54 55 56 57")

# (V) DEDUCTIBLE TAXES
# ...
mfld("59", DEBIT, '59', _("Deductible VAT from purchase invoices"),
     "81 82 83", is_payable=True)
wfld("62", DEBIT, None, _("Miscellaneous corrections deductible"),
     is_payable=True)
mfld("64", DEBIT, '59', _("VAT on sales CN"), is_payable=True)

sfld("YY", DEBIT, None, _("Total of deductible taxes"),
     "59 62 64")

# Actually only one of them
sfld("71", DEBIT, None, _("Total to pay"), "XX YY")
sfld("72", CREDIT, None, _("Total to pay"), "XX YY")

# print("20170711b {}".format(DeclarationFields.get_list_items()))
