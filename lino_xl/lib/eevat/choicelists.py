# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma 6 Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from lino_xl.lib.ledger.utils import DEBIT, CREDIT

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
# add('11', _("Private person (reduced)"), 'reduced', NAT)
add('20', _("Subject to VAT"), 'subject', NAT, needs_vat_id=True)
add('25', _("Co-contractor"), 'cocontractor', NAT, needs_vat_id=True)
add('30', _("Intra-community"), 'intracom', EU, needs_vat_id=True)
# add('31', _("Delay in collection"), 'delayed', EU) # report de perception
# add('40', _("Inside EU"), 'inside', EU)
add('50', _("Outside EU"), 'outside', INT)
add('60', _("Exempt"), 'exempt', item_vat=False)
if False:  # tim2lino can need it
    add('70', _("Germany"), 'de')
    add('71', _("Luxemburg"), 'lu')

VatRules.clear()
add = VatRules.add_item
add('normal',  '0.20', NAT,  'purchases', None,       CommonAccounts.vat_deductible)
add('reduced', '0.09', NAT,  'purchases', None,       CommonAccounts.vat_deductible)
add('normal',  '0.20', EU,   'purchases', 'intracom', CommonAccounts.vat_deductible, CommonAccounts.vat_returnable)
add('reduced', '0.09', EU,   'purchases', 'intracom', CommonAccounts.vat_deductible, CommonAccounts.vat_returnable)
# add('normal',  '0.20', EU,   'sales',     'intracom', CommonAccounts.vat_due, CommonAccounts.vat_returnable)
# add('reduced', '0.09', EU,   'sales',     'intracom', CommonAccounts.vat_due, CommonAccounts.vat_returnable)
add('normal',  '0.00', EU,   'sales',     'intracom')
add('reduced', '0.00', EU,   'sales',     'intracom')
add('reduced', '0.09', None, 'sales',     None,       CommonAccounts.vat_due)
add('normal',  '0.20', None, 'sales',     None,       CommonAccounts.vat_due)
add()

VatColumns.clear()
add = VatColumns.add_item
add('00', _("Sales with 20% VAT"), CommonAccounts.sales)
add('01', _("Sales with 9% VAT"), CommonAccounts.sales)
add('02', _("Sales with 0% VAT"), CommonAccounts.sales)
add('40', _("VAT due"), CommonAccounts.vat_due)
add('41', _("VAT returnable"), CommonAccounts.vat_returnable)
add('50', _("VAT deductible"), CommonAccounts.vat_deductible)
add('51', _("VAT deductible import"), CommonAccounts.vat_deductible)
add('52', _("VAT deductible real estate"), CommonAccounts.vat_deductible)
add('53', _("VAT deductible vehicles 100%"), CommonAccounts.vat_deductible)
add('54', _("VAT deductible vehicles"), CommonAccounts.vat_deductible)
add('81', _("Purchase of goods"), CommonAccounts.purchase_of_goods)
add('82', _("Purchase of services"), CommonAccounts.purchase_of_services)
add('83', _("Purchase of investments"), CommonAccounts.purchase_of_investments)


class DeclarationFields(DeclarationFieldsBase):
    pass

# afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field

# https://www.riigiteataja.ee/aktilisa/1060/1201/7010/Lisa%201.pdf#

# value, dc, vat_columns, text

mfld("1", CREDIT, '00', "20% määraga maksustatavad toimingud ja tehingud")
mfld("2", CREDIT, '01', "9% määraga maksustatavad toimingud ja tehingud")
mfld("3", CREDIT, '02', "0% määraga maksustatavad toimingud ja tehingud, sh")
mfld("31", CREDIT, '02',
    "1) kauba ühendusesisene käive ja teise liikmesriigi maksukohustuslasele / "
    "piiratud maksukohustuslasele osutatud teenuste käive kokku, sh",
    vat_regimes="intracom")
mfld("311", CREDIT, '02', "kauba ühendusesisene käive", vat_regimes="intracom")
mfld("32", CREDIT, '02', "2) kauba eksport, sh", vat_regimes="!intracom")
mfld("321", CREDIT, '02', "käibemaksutagastusega müük reisijale", vat_regimes="!intracom")
mfld("4", CREDIT, '40', "Käibemaks kokku (20% lahtrist 1 + 9% lahtrist 2)")
mfld("41", CREDIT, '41', "Impordilt tasumisele kuuluv käibemaks")
mfld("5", CREDIT, '50', "Kokku sisendkäibemaksusumma, mis on seadusega lubatud maha arvata, sh")
mfld("51", CREDIT, '51', "1) impordilt tasutud või tasumisele kuuluv käibemaks")
mfld("52", CREDIT, '52', "2) põhivara soetamiselt tasutud või tasumisele kuuluv käibemaks")
mfld("53", CREDIT, '53',
    "3) ettevõtluses (100%) kasutatava sõiduauto soetamiselt ja sellise"
    "sõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselt"
    "tasutud või tasumisele kuuluv käibemaks")
mfld("54", CREDIT, '54',
    "4) osaliselt ettevõtluses kasutatava sõiduauto soetamiselt ja sellise"
    "sõiduauto tarbeks kaupade soetamiselt ja teenuste saamiselt"
    "tasutud või tasumisele kuuluv käibemaks")

mfld("6", CREDIT, '52', "Kauba ühendusesisene soetamine ja teise liikmesriigi maksukohustuslaselt saadud teenused kokku, sh")
mfld("61", CREDIT, '52', "1) kauba ühendusesisene soetamine")
mfld("7", CREDIT, '52', "Muu kauba soetamine ja teenuse saamine, mida maksustatakse käibemaksuga, sh")
mfld("71", CREDIT, '52', "1) erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetallija metalltoodete soetamine (KMS § 41¹)")

mfld("8", CREDIT, '52', "Maksuvaba käive")
mfld("9", CREDIT, '52',
    "Erikorra alusel maksustatava kinnisasja, metallijäätmete, väärismetalli ja "
    "metalltoodetekäive (KMS § 411) ning teises liikmesriigis paigaldatava või "
    "kokkupandava kauba maksustatav väärtus")

wfld("10", CREDIT, None, "Täpsustused -", is_payable=True)
wfld("11", DEBIT, None, "Täpsustused +", is_payable=True)
sfld("12", DEBIT, None,
    "Tasumisele kuuluv käibemaks (lahter 4 + lahter 41 - lahter 5 + "
    "lahter 10 - lahter 11)", is_payable=True)
sfld("13", CREDIT, None,
    "Enammakstud käibemaks (lahter 4 + lahter 41 - lahter 5 + "
    "lahter 10 - lahter 11)", is_payable=True)
