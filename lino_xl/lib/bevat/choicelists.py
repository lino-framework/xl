# -*- coding: UTF-8 -*-
# Copyright 2012-2020 Rumma 6 Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_xl.lib.ledger.utils import DC

from lino.api import dd, rt, _

from lino_xl.lib.vat.choicelists import DeclarationFieldsBase
from lino_xl.lib.vat.choicelists import VatColumns
from lino_xl.lib.vat.choicelists import VatRegimes, VatAreas, VatRules
from lino_xl.lib.ledger.choicelists import CommonAccounts

NAT = VatAreas.national
EU = VatAreas.eu
INT = VatAreas.international

VatRegimes.clear()
add = VatRegimes.add_item
add('10', _("Private person"), 'normal')
add('11', _("Private person (reduced)"), 'reduced', NAT)
add('20', _("Subject to VAT"), 'subject', NAT, needs_vat_id=True)
add('25', _("Co-contractor"), 'cocontractor', NAT, needs_vat_id=True)
add('30', _("Intra-community"), 'intracom', EU, needs_vat_id=True)
add('31', _("Delay in collection"), 'delayed', EU, needs_vat_id=True) # report de perception
add('40', _("Inside EU"), 'inside', EU)
add('50', _("Outside EU"), 'outside', INT)
add('60', _("Exempt"), 'exempt', item_vat=False)
if True:  # tim2lino can need it
    add('70', _("Germany"), 'de')
    add('71', _("Luxemburg"), 'lu')


VAT_CLASSES_AND_RATES = [("services", "0.21"), ("goods", "0.21"), ("reduced", "0.07")]
VatRules.clear()
add = VatRules.add_item
for vat_class, rate in VAT_CLASSES_AND_RATES:
    add(vat_class,  rate, NAT,  'purchases', 'subject',  CommonAccounts.vat_deductible)
    add(vat_class,  rate, EU,   'purchases', 'intracom', CommonAccounts.vat_deductible, CommonAccounts.vat_returnable)
    add(vat_class,  rate, NAT,  'purchases', 'cocontractor', CommonAccounts.vat_deductible, CommonAccounts.vat_returnable)
    add(vat_class,  rate, None, 'sales',     None,       CommonAccounts.vat_due)

add()


VatColumns.clear()
add = VatColumns.add_item
add('00', _("Sales basis 0"))
add('01', _("Sales basis 1"))
add('02', _("Sales basis 2"))
add('03', _("Sales basis 3"), CommonAccounts.sales)
add('54', _("VAT due"), CommonAccounts.vat_due)
add('55', _("VAT returnable"), CommonAccounts.vat_returnable)
add('59', _("VAT deductible"), CommonAccounts.vat_deductible)
add('81', _("Purchase of goods"), CommonAccounts.purchase_of_goods)
add('82', _("Purchase of services"), CommonAccounts.purchase_of_services)
add('83', _("Purchase of investments"), CommonAccounts.purchase_of_investments)



class DeclarationFields(DeclarationFieldsBase):
    pass

# afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field

# (II) sales base
mfld("00", DC.credit, '00', _("Sales 0%"))
mfld("01", DC.credit, '01', _("Sales 6%"))
mfld("02", DC.credit, '02', _("Sales 12%"))
mfld("03", DC.credit, '03', _("Sales 20%"))
mfld("44", DC.credit, "00 01 02 03", _("Sales located inside EU"),
      vat_regimes="inside")
mfld("45", DC.credit, "00 01 02 03",  _("Sales to co-contractors"),
      vat_regimes="cocontractor")
mfld("46", DC.credit, "00 01 02 03", _("Sales intracom and ABC"),
      vat_regimes="intracom")
mfld("47", DC.credit, "00 01 02 03", _("Sales 47"),
      vat_regimes="intracom")
mfld("48", DC.debit, "00 01 02 03", _("CN sales 48"))
mfld("49", DC.debit, "00 01 02 03", _("CN sales 49"))

# (III) purchases base

mfld("81", DC.debit, '81', _("Ware"))
mfld("82", DC.debit, '82', _("Services"))
mfld("83", DC.debit, '83', _("Investments"))

mfld("84", DC.credit, "81 82 83",
      _("CN purchases on operations in 86 and 88"),
      vat_regimes="intracom", both_dc=False)
mfld("85", DC.credit, "81 82 83", _("CN purchases on other operations"),
      vat_regimes="!intracom !delayed")
mfld("86", DC.debit, "81 82 83",
      _("IC purchases and ABC sales"),
      vat_regimes="intracom")
mfld("87", DC.debit, "81 82 83", _("Other purchases in Belgium"),
      vat_regimes="cocontractor")
mfld("88", DC.debit, "81 82 83", _("IC services"),
      vat_regimes="delayed")

# (IV) DUE TAXES

mfld("54", DC.credit, '54', _("Due VAT for 01, 02 and 03"),
     vat_regimes="!intracom !delayed !cocontractor", is_payable=True)
mfld("55", DC.credit, '54', _("Due VAT for 86 and 88"),
     vat_regimes="intracom", is_payable=True)
mfld("56", DC.credit, '54',
      _("Due VAT for 87 except those covered by 57"),
     vat_regimes="cocontractor", is_payable=True)
mfld("57", DC.credit, '54',
      _("Due VAT for 87 except those covered by 57"),
      vat_regimes="delayed", is_payable=True)
wfld("61", DC.credit, None, _("Miscellaneous corrections due"),
     is_payable=True)

sfld("XX", DC.credit, None, _("Total of due taxes"),
     "54 55 56 57")

# (V) DEDUCTIBLE TAXES
# ...
mfld("59", DC.credit, '59', _("Deductible VAT from purchase invoices"),
     "81 82 83", is_payable=True)
wfld("62", DC.credit, None, _("Miscellaneous corrections deductible"),
     is_payable=True)
mfld("64", DC.credit, '59', _("VAT on sales CN"), is_payable=True)

sfld("YY", DC.credit, None, _("Total of deductible taxes"),
     "59 62 64")

# Actually only one of them
# sfld("71", DC.credit, None, _("Total to pay"), "XX YY")
sfld("72", DC.debit, None, _("Total to pay (+) or to return (-)"), "XX YY")

# print("20170711b {}".format(DeclarationFields.get_list_items()))
