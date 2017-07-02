# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Belgian VAT declaration fields.

This module may be specified as your :attr:`country_module
<lino_xl.lib.declarations.Plugin.country_module>`.

Importing this module will configure the
fields of :class:`DeclarationFields
<lino_xl.lib.declarations.choicelists.DeclarationFields>` to those of
a Belgian VAT declaration.

Based on `165-625-directives-2016.pdf
<https://finances.belgium.be/sites/default/files/downloads/165-625-directives-2016.pdf>`__
and `finances.belgium.be
<https://finances.belgium.be/fr/entreprises/tva/declaration/declaration_periodique>`__

"""

from __future__ import unicode_literals

from lino.api import dd, rt, _
from .choicelists import  DeclarationFields

from lino_xl.lib.accounts.utils import DEBIT, CREDIT
from lino_xl.lib.ledger.accounts import *

DeclarationFields.clear()
afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field

# (II) sales base 
afld("00", DEBIT, True, _("Sales 0%"))
afld("01", DEBIT, True, _("Sales 6%"))
afld("02", DEBIT, True, _("Sales 12%"))
afld("03", DEBIT, True, _("Sales 20%"))
mfld("44", DEBIT, True, _("Sales located inside EU"),
      "00 01 02 03", vat_regimes="inside")
mfld("45", DEBIT, True, _("Sales to co-contractors"),
      "00 01 02 03", vat_regimes="cocontractor")
mfld("46", DEBIT, True, _("Sales intracom and ABC"),
      "00 01 02 03", vat_regimes="intracom")
mfld("47", DEBIT, True, _("Sales 47"),
      "00 01 02 03", vat_regimes="intracom")
mfld("48", CREDIT, True, _("CN sales 48"),
      "00 01 02 03")
mfld("49", CREDIT, True, _("CN sales 49"),
      "00 01 02 03")

# (III) purchases base

afld("81", CREDIT, True, _("Ware"))
afld("82", CREDIT, True, _("Services"))
afld("83", CREDIT, True, _("Investments"))

mfld("84", DEBIT, True,
      _("CN purchases on operations in 86 and 88"),
      "81 82 83", vat_regimes="intracom")
mfld("85", DEBIT, True, _("CN purchases on other operations"),
      "81 82 83", vat_regimes="!intracom !delayed")
mfld("86", CREDIT, True,
      _("IC purchases and ABC sales"), 
      "81 82 83", vat_regimes="intracom")
mfld("87", CREDIT, True, _("Other purchases in Belgium"),
      "81 82 83", vat_regimes="cocontractor")
mfld("88", CREDIT, True, _("IC services"),
      "81 82 83", vat_regimes="delayed")

# (IV) DUE TAXES

mfld("54", CREDIT, False, _("Due VAT for 01, 02 and 03"),
      "01 02 03")
mfld("55", CREDIT, False, _("Due VAT for 86 and 88"),
      "81 82 83", vat_regimes="intracom")
mfld("56", CREDIT, False,
      _("Due VAT for 87 except those covered by 57"),
      "81 82 83")
mfld("57", CREDIT, False,
      _("Due VAT for 87 except those covered by 57"),
      "81 82 83", vat_regimes="delayed")

sfld("XX", CREDIT, False, _("Total of due taxes"),
     "54 55 56 57")

# (V) DEDUCTIBLE TAXES
# ...
mfld("59", DEBIT, False, _("Deductible VAT from purchase invoices"),
     "81 82 83")
wfld("62", DEBIT, False, _("Miscellaneous corrections"))
mfld("64", DEBIT, False, _("VAT on sales CN"),
     "01 02 03")

sfld("YY", DEBIT, False, _("Total of deductible taxes"),
     "59 62 64")

sfld("71", CREDIT, False, _("Total of deductible taxes"),
     "XX YY")

for fld in DeclarationFields.objects():
    dd.inject_field('declarations.Declaration', fld.name, fld.get_model_field())

class DeclarationDetail(dd.DetailLayout):
    main = """
    start_date end_date entry_date accounting_period partner user workflow_buttons
    c2 c2b c2c c3 c3b c4 c5
    FXX FYY F71
    VouchersByDeclaration
    """
    c2="""
    F00 
    F01 
    F02 
    F03 
    """
    c2b="""
    F44 
    F45
    F46
    """
    c2c="""
    F47
    F48
    F49
    """
    c3 = """
    F81 
    F82 
    F83
    F84 
    """
    c3b = """
    F85 
    F86 
    F87 
    F88
    """

    c4 = """
    F54
    F55 
    F56
    F57
    """
    c5 = """
    F59
    F62 
    F64
    """
    
    # fields="""
    # F00 F01 F02 F03 
    # F44 F45 F46 F47 F48 F49
    # F81 F82 F83
    # F84 F85 F86 F87 F88
    # """

if dd.is_installed('declarations'):

    rt.models.declarations.Declarations.detail_layout = DeclarationDetail()


def demo_objects():
    
    def dcl(acc, fld):
        obj = rt.models.accounts.Account.get_by_ref(acc)
        obj.declaration_field = DeclarationFields.get_by_value(fld)
        return obj

    yield dcl(SALES_ACCOUNT, '03')
    yield dcl(VAT_DUE_ACCOUNT, '54')
    yield dcl(VAT_DEDUCTIBLE_ACCOUT, '59')
    yield dcl(VAT_RETURNABLE_ACCOUNT, '55')
    # yield dcl(VATDCL_ACCOUNT, '20')
    yield dcl(PURCHASE_OF_GOODS, '81')
    yield dcl(PURCHASE_OF_SERVICES, '82')
    yield dcl(PURCHASE_OF_INVESTMENTS, '83')

