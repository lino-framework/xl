# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma 6 Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

# from django.db import models
# from django.conf import settings
#from django.utils.translation import string_concat
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
add('10', _("Not subject to VAT"), 'normal')
add('20', _("Subject to VAT"), 'subject', NAT)
add('30', _("Intracom services"), 'intracom', EU)
add('35', _("Intracom supplies"), 'intracom_supp', EU)

VatColumns.clear()
add = VatColumns.add_item
add('54', _("VAT due"))
# add('55', _("VAT returnable"))
# add('59', _("VAT deductible"))
add('71', _("Purchase of ware"))
add('72', _("Purchase of new vehicles"))
add('73', _("Purchase of excised products"))
add('75', _("Purchase of services"))
add('76', _("Other purchase"))


VatRules.clear()
add = VatRules.add_item
# country_code = dd.plugins.countries.country_code
# if country_code == "BE":
add('010', 'normal',  '0.21', EU, 'purchases', 'intracom',      CommonAccounts.vat_due, vat_returnable=True)
add('020', 'normal',  '0.21', EU, 'purchases', 'intracom_supp', CommonAccounts.vat_due, vat_returnable=True)
add('900')


class DeclarationFields(DeclarationFieldsBase):
    pass

# afld = DeclarationFields.add_account_field
sfld = DeclarationFields.add_sum_field
mfld = DeclarationFields.add_mvt_field
wfld = DeclarationFields.add_writable_field


# II. Opérations à déclarer (montant hors TVA)

mfld("71", DEBIT, '71', _("Intracom supplies"))
mfld("72", DEBIT, '72', _("New vehicles"))
mfld("73", DEBIT, '73', _("Excised products"))
mfld("75", DEBIT, '75', _("Intracom services"))
mfld("76", DEBIT, '76', _("Other operations"))
mfld("77", CREDIT, '71 72 73 75',
     _("Credit notes on 71, 72, 73 and 75"), both_dc=False)
mfld("78", DEBIT, '76',
     _("Credit notes on 76"), both_dc=False)

# III. Taxes dues et régularisations de la taxe

mfld("80", CREDIT, '54',
     _("Due VAT for 71...76"), is_payable=True)
wfld("81", CREDIT, None, _("Miscellaneous corrections due"),
     is_payable=True)
wfld("82", DEBIT, None, _("Miscellaneous corrections returnable"),
     is_payable=True)

sfld("83", CREDIT, None, _("Total to pay"), "80 81 82")

# print("20170711b {}".format(DeclarationFields.get_list_items()))
