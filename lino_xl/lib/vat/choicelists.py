# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Choicelists for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from decimal import Decimal
from lino.api import dd, _
from lino.utils.xmlgen.html import E
from lino_xl.lib.ledger.roles import LedgerStaff

from lino_xl.lib.accounts.utils import DCLABELS


class VatClasses(dd.ChoiceList):
    verbose_name = _("VAT Class")
    verbose_name_plural = _("VAT Classes")
    required_roles = dd.login_required(LedgerStaff)

add = VatClasses.add_item
add('0', _("Exempt"), 'exempt')    # post stamps, ...
add('1', _("Reduced"), 'reduced')  # food, books,...
add('2', _("Normal"), 'normal')    # everything else


class VatColumns(dd.ChoiceList):
    # to be populated by bevat, bevats, ...
    verbose_name = _("VAT column")
    verbose_name_plural = _("VAT columns")
    required_roles = dd.login_required(LedgerStaff)
    show_values = True

    

class VatRegime(dd.Choice):

    item_vat = True


class VatRegimes(dd.ChoiceList):
    verbose_name = _("VAT regime")
    verbose_name_plural = _("VAT regimes")
    item_class = VatRegime
    required_roles = dd.login_required(LedgerStaff)
    help_text = _(
        "Determines how the VAT is being handled, \
        i.e. whether and how it is to be paid.")

add = VatRegimes.add_item
add('10', _("Private person"), 'private')
add('20', _("Subject to VAT"), 'subject')
add('30', _("Intra-community"), 'intracom')
# re-populated in bevat or bevats.
# See also lino_xl.lib.vat.Plugin.default_vat_regime

# @dd.python_2_unicode_compatible
class DeclarationField(dd.Choice):
    editable = False
    vat_regimes = None
    exclude_vat_regimes = None
    vat_classes = None
    exclude_vat_classes = None
    vat_columns = None
    exclude_vat_columns = None
    is_payable = False
    
    def __init__(self, value, dc,
                 vat_columns=None,
                 # is_base,
                 text=None,
                 fieldnames='',
                 both_dc=True,
                 vat_regimes=None, vat_classes=None,
                 **kwargs):
        name = "F" + value
        # text = string_concat("[{}] ".format(value), text)
        self.help_text = text
        super(DeclarationField, self).__init__(
            value, "[{}]".format(value), name, **kwargs)
        
        # self.is_base = is_base
        self.fieldnames = fieldnames
        self.dc = dc
        self.both_dc = both_dc

        if vat_regimes:
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
            
        if vat_classes:
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
                
        if vat_columns:
            self.vat_columns = set()
            self.exclude_vat_columns = set()
            for n in vat_columns.split():
                if n.startswith('!'):
                    s = self.exclude_vat_columns
                    n = n[1:]
                else:
                    s = self.vat_columns
                v = VatColumns.get_by_value(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT column {} for field {}".format(
                            v, value))
                s.add(v)
        

    def attach(self, choicelist):
        super(DeclarationField, self).attach(choicelist)
        self.observed_fields = set()
        for n in self.fieldnames.split():
            f = choicelist.get_by_value(n)
            if f is None:
                raise Exception(
                    "Invalid observed field {} for {}".format(
                        n, self))
            self.observed_fields.add(f)
        
    def get_model_field(self):
        return dd.PriceField(
            self.text, default=Decimal, editable=self.editable,
            help_text=self.help_text)
    
    # def __str__(self):
    #     # return force_text(self.text, errors="replace")
    #     # return self.text
    #     return "[{}] {}".format(self.value, self.text)

    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        pass
    
    def collect_from_sums(self, dcl, sums, payable_sums):
        pass

class SumDeclarationField(DeclarationField):
    
    def collect_from_sums(self, dcl, field_values, payable_sums):
        tot = Decimal()
        for f in self.observed_fields:
            v = field_values[f.name]
            if f.dc == self.dc:
                tot += v
            else:
                tot += v
        field_values[self.name] = tot
        
class WritableDeclarationField(DeclarationField):
    editable = True
    def collect_from_sums(self, dcl, field_values, payable_sums):
        if self.is_payable:
            amount = field_values[self.name]
            if amount:
                if self.dc == dcl.journal.dc:
                    amount = - amount
                k = ((dcl.journal.account, None), None, None, None)
                payable_sums.collect(k, amount)

class MvtDeclarationField(DeclarationField):
    
    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        # if not mvt.account.declaration_field in self.observed_fields:
        #     return 0
        if self.vat_classes is not None:
            if not mvt.vat_class in self.vat_classes:
                return
            if mvt.vat_class in self.exclude_vat_classes:
                return
        if self.vat_columns is not None:
            if not mvt.account.vat_column in self.vat_columns:
                return
            if mvt.account.vat_column in self.exclude_vat_columns:
                return
        if self.vat_regimes is not None:
            if not mvt.vat_regime in self.vat_regimes:
                return
            if mvt.vat_regime in self.exclude_vat_regimes:
                return
        if mvt.dc == self.dc:
            amount = mvt.amount
        elif self.both_dc:
            amount = -mvt.amount
        else:
            return
        if not amount:
            return
        field_values[self.name] += amount
        if self.is_payable:
            if self.dc == dcl.journal.dc:
                amount = - amount
            k = ((mvt.account, None), mvt.project, mvt.vat_class, mvt.vat_regime)
            payable_sums.collect(k, amount)
            # k = (dcl.journal.account, None, None, None)
            # payable_sums.collect(k, amount)
    

# class AccountDeclarationField(MvtDeclarationField):
#     pass
    # def __init__(self, value, dc, vat_columns, *args, **kwargs):
    #     # kwargs.update(fieldnames=value)
    #     kwargs.update(vat_columns=vat_columns)
    #     super(AccountDeclarationField, self).__init__(
    #         value, dc, *args, **kwargs)



class DeclarationFieldsBase(dd.ChoiceList):
    verbose_name_plural = _("Declaration fields")
    item_class = DeclarationField
    column_names = "value name text description *"
    
    # @classmethod    
    # def add_account_field(cls, *args, **kwargs):
    #     cls.add_item_instance(
    #         AccountDeclarationField(*args, **kwargs))
        
    @classmethod    
    def add_mvt_field(cls, *args, **kwargs):
        cls.add_item_instance(
            MvtDeclarationField(*args, **kwargs))
        
    @classmethod    
    def add_sum_field(cls, *args, **kwargs):
        cls.add_item_instance(
            SumDeclarationField(*args, **kwargs))


    @classmethod    
    def add_writable_field(cls, *args, **kwargs):
        cls.add_item_instance(
            WritableDeclarationField(*args, **kwargs))
        

    @dd.displayfield(_("Description"))
    def description(cls, fld, ar):
        if ar is None:
            return ''
        elems = [fld.help_text, E.br()]
        def x(label, lst, xlst):
            if lst is None:
                return
            spec = ' '.join([i.name or i.value for i in lst])
            if xlst is not None:
                spec += ' ' + ' '.join([
                    "!"+(i.name or i.value) for i in xlst])
            spec = spec.strip()
            if spec:
                elems.extend([label, " ", spec, E.br()])

        x(_("columns"), fld.vat_columns, fld.exclude_vat_columns)
        x(_("regimes"), fld.vat_regimes, fld.exclude_vat_regimes)
        x(_("classes"), fld.vat_classes, fld.exclude_vat_classes)


        elems += [
            fld.__class__.__name__, ' ',
            DCLABELS[fld.dc], 
            "" if fld.both_dc else " only",
            E.br()]

        if fld.observed_fields:
            elems += [
                _("Sum of"), ' ',
                ' '.join([i.name for i in fld.observed_fields]),
                E.br()]

        return E.div(*elems)

