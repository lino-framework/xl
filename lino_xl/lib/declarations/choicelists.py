# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Declaration fields.
"""

from __future__ import unicode_literals

from decimal import Decimal

# from django.db import models
# from django.conf import settings
from django.utils.translation import string_concat

from lino.api import dd

from lino_xl.lib.vat.choicelists import VatRegimes, VatClasses


# @dd.python_2_unicode_compatible
class DeclarationField(dd.Choice):
    editable = False
    vat_regimes = None
    exclude_vat_regimes = None
    vat_classes = None
    exclude_vat_classes = None
    
    def __init__(self, value, dc, is_base, text=None,
                 fieldnames='', both_dc=False,
                 vat_regimes=None, vat_classes=None,
                 **kwargs):
        name = "F" + value
        # text = string_concat("[{}] ".format(value), text)
        self.help_text = text
        super(DeclarationField, self).__init__(
            value, "[{}]".format(value), name, **kwargs)
        
        self.is_base = is_base
        self.fieldnames = fieldnames
        self.dc = dc
        self.both_dc = both_dc

        if vat_regimes is not None:
            self.vat_regimes = set()
            self.exclude_vat_regimes = set()
            for n in vat_regimes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_regimes
                    n = n[1:]
                else:
                    s = self.vat_regimes
                v = VatRegimes.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT regime {} for field {}".format(
                            v, value))
                s.add(v)
            
        if vat_classes is not None:
            self.vat_classes = set()
            self.exclude_vat_classes = set()
            for n in vat_classes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_classes
                    n = n[1:]
                else:
                    s = self.vat_classes
                v = VatClasses.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT class {} for field {}".format(
                            v, value))
                s.add(v)
        

    def attach(self, choicelist):
        super(DeclarationField, self).attach(choicelist)
        self.observed_fields = set()
        for v in self.fieldnames.split():
            f = choicelist.get_by_value(v)
            if f is None:
                raise Exception("Invalid declaration field {}".format(v))
            self.observed_fields.add(f)
        
    # def __str__(self):
    #     # return force_text(self.text, errors="replace")
    #     # return self.text
    #     return "[{}] {}".format(self.value, self.text)

    def collect_movement(self, dcl, mvt):
        return 0
    
    def collect_from_sums(self, dcl, sums):
        pass

    def get_model_field(self):
        return dd.PriceField(
            self.text, default=Decimal, editable=self.editable,
            help_text=self.help_text)
    
class SumDeclarationField(DeclarationField):
    
    def collect_from_sums(self, dcl, sums):
        tot = Decimal()
        for f in self.observed_fields:
            tot += sums[f.name]
        sums[self.name] = tot
        
class MvtDeclarationField(DeclarationField):
    
    def collect_movement(self, dcl, mvt):
        if not mvt.account.declaration_field in self.observed_fields:
            return 0
        if self.vat_classes is not None:
            if not mvt.vat_class in self.vat_classes:
                return 0
            if mvt.vat_class in self.exclude_vat_classes:
                return 0
        if self.vat_regimes is not None:
            if not mvt.vat_regime in self.vat_regimes:
                return 0
            if mvt.vat_regime in self.exclude_vat_regimes:
                return 0
        if mvt.dc is self.dc:
            return mvt.amount
        elif self.both_dc:
            return mvt.amount
        else:
            return 0
            
class AccountDeclarationField(MvtDeclarationField):
    
    def __init__(self, value, *args, **kwargs):
        kwargs.update(observed_fields=value)
        super(AccountDeclarationField, self).__init__(value, *args, **kwargs)


class DeclarationFields(dd.ChoiceList):

    item_class = DeclarationField
    
    @classmethod    
    def add_account_field(cls, *args, **kwargs):
        DeclarationFields.add_item_instance(AccountDeclarationField(*args, **kwargs))
        
    @classmethod    
    def add_mvt_field(cls, *args, **kwargs):
        DeclarationFields.add_item_instance(MvtDeclarationField(*args, **kwargs))
        
    @classmethod    
    def add_sum_field(cls, *args, **kwargs):
        DeclarationFields.add_item_instance(SumDeclarationField(*args, **kwargs))
