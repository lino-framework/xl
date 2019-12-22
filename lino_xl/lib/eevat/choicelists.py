# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma 6 Ko Ltd
# License: BSD (see file COPYING for details)

from lino_xl.lib.ledger.utils import DEBIT, CREDIT

from lino_xl.lib.vat.choicelists import DeclarationFieldsBase
from lino_xl.lib.vat.choicelists import VatColumns
from lino_xl.lib.vat.choicelists import VatRegimes, VatAreas, VatRules
from lino_xl.lib.ledger.choicelists import CommonAccounts

from lino.api import dd, rt, _

NAT = VatAreas.national
EU = VatAreas.eu
INT = VatAreas.international

VatRegimes.clear()
add = VatRegimes.add_item
add('10', _("Private person"), 'normal')
# add('11', _("Private person (reduced)"), 'reduced', NAT)
add('20', _("Subject to VAT"), 'subject', NAT, needs_vat_id=True)
add('25', _("Co-contractor"), 'cocontractor', NAT, needs_vat_id=True)
add('30', _("Intra-community"), 'intracom', EU, needs_vat_id=True)
# add('31', _("Delay in collection"), 'delayed', EU) # report de perception
# add('40', _("Inside EU"), 'inside', EU)
add('40', _("Tax-free"), 'tax_free')
add('50', _("Outside EU"), 'outside', INT)
add('60', _("Exempt"), 'exempt', item_vat=False)  # army, ...
if False:  # tim2lino can need it
    add('70', _("Germany"), 'de')
    add('71', _("Luxemburg"), 'lu')

VAT_CLASSES_AND_RATES = [
    ("services", "0.20"), ("goods", "0.20"),
    ("real_estate", "0.20"), ("vehicles", "0.20"),
    ("reduced", "0.09")]
VatRules.clear()
add = VatRules.add_item
#   vat_class      rate vat_area trade_type   vat_regime  vat_account   vat_returnable_account vat_returnable
add(None, '0', None, None, "exempt")


for vat_class, rate in VAT_CLASSES_AND_RATES:
    for vat_regime, area in [('intracom', EU), ('cocontractor', NAT)]:
        add(vat_class, rate, area, 'purchases', vat_regime, CommonAccounts.vat_deductible, CommonAccounts.vat_returnable)
        add(vat_class, rate, area, 'sales',     vat_regime, CommonAccounts.vat_due, CommonAccounts.vat_returnable)

for vat_class, rate in VAT_CLASSES_AND_RATES:
    add(vat_class, rate, NAT,  'purchases', None, CommonAccounts.vat_deductible)
    add(vat_class, rate, None, 'sales', None,  CommonAccounts.vat_due)

add()  # allow any other combination with rate 0


VatColumns.clear()
add = VatColumns.add_item
add('10', _("Sales turnover"), CommonAccounts.sales)
# add('01', _("Sales with 20% VAT"), CommonAccounts.sales)
# add('02', _("Sales with 9% VAT"), CommonAccounts.sales)
# add('03', _("Sales with 0% VAT"), CommonAccounts.sales)
add('40', _("VAT due"), CommonAccounts.vat_due)
add('41', _("VAT returnable"), CommonAccounts.vat_returnable)
add('50', _("VAT deductible"), CommonAccounts.vat_deductible)
add('60', _("Purchase of goods"), CommonAccounts.purchase_of_goods)
add('61', _("Other purchases"), CommonAccounts.purchase_of_services)
# add('62', _("Purchase of services"), CommonAccounts.purchase_of_services)
# add('63', _("Purchase of investments"), CommonAccounts.purchase_of_investments)


class DeclarationFields(DeclarationFieldsBase):
    pass

# afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field

# https://www.riigiteataja.ee/aktilisa/1060/1201/7010/Lisa%201.pdf#

# value dc vat_columns text // fieldnames both_dc vat_regimes vat_classes

mfld("1",  CREDIT, '10', "20% määraga maksustatavad toimingud ja tehingud",
    vat_classes="goods services", vat_regimes="!exempt !tax_free !intracom !cocontractor")
mfld("2",  CREDIT, '10', "9% määraga maksustatavad toimingud ja tehingud",
    vat_classes="reduced", vat_regimes="!exempt !tax_free !intracom !cocontractor")

mfld("3",  CREDIT, '10', "0% määraga maksustatavad toimingud ja tehingud, sh",
    vat_regimes="exempt tax_free intracom cocontractor")

mfld("31", CREDIT, '10',
    "1) kauba ühendusesisene käive ja teise liikmesriigi maksukohustuslasele / "
    "piiratud maksukohustuslasele osutatud teenuste käive kokku, sh",
    vat_regimes="intracom cocontractor")
mfld("311", CREDIT, '10', "1) kauba ühendusesisene käive",
    vat_regimes="intracom")

mfld("32",  CREDIT, '10', "2) kauba eksport, sh",
    vat_regimes="tax_free exempt")
mfld("321", CREDIT, '10', "1) käibemaksutagastusega müük reisijale",
    vat_regimes="tax_free")

mfld("4",  CREDIT, '40',
    "Käibemaks kokku (20% lahtrist 1 + 9% lahtrist 2)")
mfld("41", DEBIT, '41',
    "Impordilt tasumisele kuuluv käibemaks")

mfld("5",  CREDIT, '50',
    "Kokku sisendkäibemaksusumma, mis on seadusega lubatud maha arvata, sh")
mfld("51", CREDIT, '50',
    "1) impordilt tasutud või tasumisele kuuluv käibemaks",
    vat_regimes="intracom")
mfld("52", CREDIT, '50',
    "2) põhivara soetamiselt tasutud või tasumisele kuuluv käibemaks",
    vat_classes="real_estate")
mfld("53", CREDIT, '50',
    "3) ettevõtluses (100%) kasutatava sõiduauto soetamiselt ja sellise"
    "sõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselt"
    "tasutud või tasumisele kuuluv käibemaks",
    vat_classes="vehicles")
mfld("54", CREDIT, '50',
    "4) osaliselt ettevõtluses kasutatava sõiduauto soetamiselt ja sellise"
    "sõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselt"
    "tasutud või tasumisele kuuluv käibemaks",
    vat_classes="vehicles")  #TODO: add an estonia-specific second vat category for vehicles?

mfld("6", DEBIT, '60',
    "Kauba ühendusesisene soetamine ja teise liikmesriigi "
    "maksukohustuslaselt saadud teenused kokku, sh")
mfld("61", DEBIT, '60', "1) kauba ühendusesisene soetamine",
    vat_regimes="intracom", vat_classes="goods")

mfld("7",  DEBIT, '60',
    "Muu kauba soetamine ja teenuse saamine, mida maksustatakse käibemaksuga, sh",
    vat_regimes="!intracom", vat_classes="!goods")
mfld("71", DEBIT, '60',
    "1) erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli "
    "ja metalltoodete soetamine (KMS § 41¹)",
    vat_regimes="!intracom", vat_classes="!goods") # not yet handled

mfld("8", DEBIT, '60', "Maksuvaba käive", vat_classes="exempt")
mfld("9", DEBIT, '61',
    "Erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja "
    "metalltoodete käive (KMS § 411) ning teises liikmesriigis paigaldatava või "
    "kokkupandava kauba maksustatav väärtus")

wfld("10", CREDIT, None, "Täpsustused (-)", editable=True)
wfld("11", DEBIT, None, "Täpsustused (+)", editable=True)

sfld("13", CREDIT, None,
    "Tasumisele kuuluv(+) või enammakstud (-) käibemaks "
    "(lahter 4 + lahter 41 - lahter 5 + lahter 10 - lahter 11)",
    is_payable=True, fieldnames="4 41 -5 10 -11")
