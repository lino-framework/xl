# Copyright 2012-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Database models for this plugin.

"""

from __future__ import unicode_literals

# from decimal import Decimal

# from django.db import models
# from django.conf import settings

from lino.api import dd, _

from lino_xl.lib.vat.mixins import VatDeclaration

from .choicelists import DeclarationFields

DEMO_JOURNAL_NAME = "VAT"
    
class Declaration(VatDeclaration):
    
    fields_list = DeclarationFields
    
    class Meta:
        app_label = 'bevats'
        verbose_name = _("Special Belgian VAT declaration")
        verbose_name_plural = _("Special Belgian VAT declarations")
        
from lino_xl.lib.vat.mixins import DECLARED_IN

if DECLARED_IN:
    dd.inject_field('ledger.Voucher',
                    'declared_in',
                    dd.ForeignKey(Declaration,
                                  blank=True, null=True))

for fld in DeclarationFields.get_list_items():
    dd.inject_field('bevats.Declaration', fld.name, fld.get_model_field())

