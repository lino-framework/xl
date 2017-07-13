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
from lino_xl.lib.ledger.roles import LedgerStaff


class VatClasses(dd.ChoiceList):
    """
    A VAT class is a direct or indirect property of a trade object
    (e.g. a Product) which determines the VAT *rate* to be used.  It
    does not contain the actual rate because this still varies
    depending on your country, the time and type of the operation, and
    possibly other factors.

    Default classes are:

    .. attribute:: exempt

    .. attribute:: reduced

    .. attribute:: normal


    """
    verbose_name = _("VAT Class")
    verbose_name_plural = _("VAT Classes")
    required_roles = dd.login_required(LedgerStaff)

add = VatClasses.add_item
add('0', _("Exempt"), 'exempt')    # post stamps, ...
add('1', _("Reduced"), 'reduced')  # food, books,...
add('2', _("Normal"), 'normal')    # everything else


class VatColumns(dd.ChoiceList):
    verbose_name = _("VAT column")
    verbose_name_plural = _("VAT columns")
    required_roles = dd.login_required(LedgerStaff)
    
add = VatColumns.add_item
add('00', _("Sales basis 0"))
add('01', _("Sales basis 1"))
add('02', _("Sales basis 2"))
add('03', _("Sales basis 3"))
add('54', _("VAT due"))
add('55', _("VAT returnable"))
add('59', _("VAT deductible"))
add('81', _("Purchase of goods"))
add('82', _("Purchase of services"))
add('83', _("Purchase of investments"))


class VatRegime(dd.Choice):
    "Base class for choices of :class:`VatRegimes`."

    item_vat = True
    "Whether unit prices are VAT included or not."


class VatRegimes(dd.ChoiceList):
    """
    The VAT regime is a classification of the way how VAT is being
    handled, e.g. whether and how it is to be paid.

    """
    verbose_name = _("VAT regime")
    verbose_name_plural = _("VAT regimes")
    item_class = VatRegime
    required_roles = dd.login_required(LedgerStaff)
    help_text = _(
        "Determines how the VAT is being handled, \
        i.e. whether and how it is to be paid.")

add = VatRegimes.add_item
add('10', _("Private person"), 'private')
add('11', _("Private person (reduced)"), 'reduced')
add('20', _("Subject to VAT"), 'subject')
add('25', _("Co-contractor"), 'cocontractor')
add('30', _("Intra-community"), 'intracom')
add('31', _("Delay in collection"), 'delayed') # report de perception
add('40', _("Inside EU"), 'inside')
add('50', _("Outside EU"), 'outside')
add('60', _("Exempt"), 'exempt', item_vat=False)
add('70', _("Germany"), 'de')
add('71', _("Luxemburg"), 'lu')



# @dd.python_2_unicode_compatible
class DeclarationField(dd.Choice):
    editable = False
    vat_regimes = None
    exclude_vat_regimes = None
    vat_classes = None
    exclude_vat_classes = None
    vat_columns = None
    exclude_vat_columns = None
    
    def __init__(self, value, dc,
                 vat_columns=None,
                 # is_base,
                 text=None,
                 fieldnames='',
                 both_dc=False,
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
                
        if vat_columns is not None:
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
        
    # def __str__(self):
    #     # return force_text(self.text, errors="replace")
    #     # return self.text
    #     return "[{}] {}".format(self.value, self.text)

    def collect_movement(self, dcl, mvt):
        return 0
    
    def collect_wanted_movements(self, dcl, mvt_dict):
        pass
    
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
        # if not mvt.account.declaration_field in self.observed_fields:
        #     return 0
        if self.vat_classes is not None:
            if not mvt.vat_class in self.vat_classes:
                return 0
            if mvt.vat_class in self.exclude_vat_classes:
                return 0
        if self.vat_columns is not None:
            if not mvt.account.vat_column in self.vat_columns:
                return 0
            if mvt.account.vat_column in self.exclude_vat_columns:
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
        kwargs.update(fieldnames=value)
        super(AccountDeclarationField, self).__init__(
            value, *args, **kwargs)


class WritableDeclarationField(DeclarationField):
    editable = True


class DeclarationFieldsBase(dd.ChoiceList):

    item_class = DeclarationField
    
    @classmethod    
    def add_account_field(cls, *args, **kwargs):
        cls.add_item_instance(
            AccountDeclarationField(*args, **kwargs))
        
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

