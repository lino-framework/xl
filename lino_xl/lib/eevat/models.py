# Copyright 2012-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

# from decimal import Decimal

# from django.db import models
# from django.conf import settings

from lino.api import dd, _

from lino_xl.lib.vat.mixins import VatDeclaration

# vat = dd.resolve_app('vat')
# ledger = dd.resolve_app('ledger')

# ZERO = Decimal()

from .choicelists import DeclarationFields

DEMO_JOURNAL_NAME = "VAT"

# print("20170711a {}".format(DeclarationFields.get_list_items()))

class Declaration(VatDeclaration):
    
    fields_list = DeclarationFields
    
    class Meta:
        app_label = 'eevat'
        verbose_name = _("Estonian VAT declaration")
        verbose_name_plural = _("Estonian VAT declarations")
        
# if dd.is_installed('declarations'): # avoid autodoc failure
#     # importing the country module will fill DeclarationFields
#     import_module(dd.plugins.declarations.country_module)

from lino_xl.lib.vat.mixins import DECLARED_IN

if DECLARED_IN:
    dd.inject_field('ledger.Voucher',
                    'declared_in',
                    dd.ForeignKey(Declaration,
                                  blank=True, null=True))

# dd.inject_field('ledger.Account',
#                 'declaration_field',
#                 DeclarationFields.field(blank=True, null=True))

# dd.inject_field('ledger.Journal',
#                 'declared',
#                 models.BooleanField(default=True))

for fld in DeclarationFields.get_list_items():
    dd.inject_field('eevat.Declaration', fld.name, fld.get_model_field())

