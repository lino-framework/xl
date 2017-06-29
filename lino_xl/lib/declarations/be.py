# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Belgian VAT declaration fields.

Based on 
https://finances.belgium.be/sites/default/files/downloads/165-625-directives-2016.pdf

General info:
https://finances.belgium.be/fr/entreprises/tva/declaration/declaration_periodique



"""

from __future__ import unicode_literals

from lino.api import dd, rt, _
from .choicelists import  DeclarationFields

from lino_xl.lib.accounts.utils import DEBIT, CREDIT
from lino_xl.lib.ledger.accounts import *

    
DeclarationFields.fields_layout = dd.Panel("""
    F00 F01 F02 F03 
    F44 F45 F46 F47 F48 F49
    F81 F82 F83
    F84 F85 F86 F87 F88
    """)
acase = DeclarationFields.add_account_field
scase = DeclarationFields.add_sum_field
mcase = DeclarationFields.add_mvt_field

# (I) sales base 
acase("00", DEBIT, True, _("Sales 0%"))
acase("01", DEBIT, True, _("Sales 6%"))
acase("02", DEBIT, True, _("Sales 12%"))
acase("03", DEBIT, True, _("Sales 20%"))
mcase("44", DEBIT, True, _("Sales located inside EU"),
      "00 01 02 03", vat_regimes="inside")
mcase("45", DEBIT, True, _("Sales to co-contractors"),
      "00 01 02 03", vat_regimes="cocontractor")
mcase("46", DEBIT, True, _("Sales intracom and ABC"),
      "00 01 02 03", vat_regimes="intracom")
mcase("47", DEBIT, True, _("Sales 47"),
      "00 01 02 03", vat_regimes="intracom")
mcase("48", CREDIT, True, _("CN sales 48"),
      "00 01 02 03")
mcase("49", CREDIT, True, _("CN sales 49"),
      "00 01 02 03")

# (III) purchases base 

acase("81", CREDIT, True, _("Ware"))
acase("82", CREDIT, True, _("Services"))
acase("83", CREDIT, True, _("Investments"))

mcase("84", DEBIT, True,
      _("CN purchases on operations in 86 and 88"),
      "81 82 83", vat_regimes="intracom")
mcase("85", DEBIT, True, _("CN purchases on other operations"),
      "81 82 83", vat_regimes="!intracom !delayed")
mcase("86", CREDIT, True,
      _("IC purchases and ABC sales"), 
      "81 82 83", vat_regimes="intracom")
mcase("87", CREDIT, True, _("Other purchases in Belgium"),
      "81 82 83", vat_regimes="cocontractor")
mcase("88", CREDIT, True, _("IC services"),
      "81 82 83", vat_regimes="delayed")

# (IV) DUE TAXES

mcase("54", CREDIT, False, _("Due VAT for 01, 02 and 03"),
      "01 02 03")
mcase("55", CREDIT, False, _("Due VAT for 86 and 88"),
      "81 82 83", vat_regimes="intracom")
mcase("56", CREDIT, False,
      _("Due VAT for 87 except those covered by 57"),
      "81 82 83")
mcase("57", CREDIT, False,
      _("Due VAT for 87 except those covered by 57"),
      "81 82 83", vat_regimes="delayed")

# (V) DEDUCTIBLE TAXES
# ...
mcase("59", CREDIT, False, _("Deductible VAT from purchase invoices"),
      "81 82 83")
mcase("64", DEBIT, False, _("VAT on sales CN"),
      "01 02 03")

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

