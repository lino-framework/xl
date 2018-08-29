# -*- coding: UTF-8 -*-
# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.db import models

from lino.api import dd, rt, _
from lino_xl.lib.ledger.roles import LedgerStaff
from lino_xl.lib.ledger.models import DebitOrCreditField
from lino_xl.lib.ledger.utils import DEBIT, CREDIT


class SheetTypes(dd.ChoiceList):
    verbose_name = _("Sheet type")
    verbose_name_plural = _("Sheet types")

add = SheetTypes.add_item
add("B", _("Balance sheet"), 'balance')
add("R", _("Income statement"), 'results')


class CommonItem(dd.Choice):
    show_values = True
    sheet_type = None
    dc = None
    _instance = None
    mirror_ref = None
    
    
    def __init__(self, value, text, name, dc, sheet_type, **kwargs):
        # the class attribute `name` ís used as value
        super(CommonItem, self).__init__(value, text, name, **kwargs)
        self.sheet_type = SheetTypes.get_by_name(sheet_type)
        self.dc = dc

    if dd.is_installed('sheets'):
    
        def create_object(self, **kwargs):
            kwargs.update(dd.str2kw('designation', self.text))
            kwargs.update(dc=self.dc)
            kwargs.update(common_item=self)
            kwargs.update(sheet_type=self.sheet_type)
            kwargs.update(mirror_ref=self.mirror_ref)
            return rt.models.sheets.Item(ref=self.value, **kwargs)

        def get_object(self):
            # return rt.models.ledger.Account.objects.get(ref=self.value)
            if self._instance is None:
                Item = rt.models.sheets.Item
                try:
                    self._instance = Item.objects.get(common_item=self)
                except Item.DoesNotExist:
                    return None
            return self._instance
    else:

        def get_object(self):
            return None


class CommonItems(dd.ChoiceList):
    verbose_name = _("Common sheet item")
    verbose_name_plural = _("Common sheet item")
    item_class = CommonItem
    column_names = 'value name text sheet_type dc db_object'
    required_roles = dd.login_required(LedgerStaff)

    @dd.virtualfield(models.CharField(_("Sheet type"), max_length=20))
    def sheet_type(cls, choice, ar):
        return choice.sheet_type

    @dd.virtualfield(DebitOrCreditField(_("D/C")))
    def dc(cls, choice, ar):
        return choice.dc

    @dd.virtualfield(dd.ForeignKey('sheets.Item'))
    def db_object(cls, choice, ar):
        return choice.get_object()


def mirror(a, b):
    a = CommonItems.get_by_value(a)
    b = CommonItems.get_by_value(b)
    if a.dc == b.dc:
        raise Exception("Mirroring items must have opposite D/C")
    a.mirror_ref = b.value
    b.mirror_ref = a.value

add = CommonItems.add_item

# Aktiva (Vermögen)
add('1', _("Assets"), 'assets', DEBIT, 'balance')
# Umlaufvermögen
add('10', _("Current assets"), None, DEBIT, 'balance')  
add('1000', _("Customers receivable"), 'customers', DEBIT, 'balance')
add('1010', _("Taxes receivable"), None, DEBIT, 'balance')
add('1020', _("Cash and cash equivalents"), None, DEBIT, 'balance')
add('1030', _("Current transfers"), None, DEBIT, 'balance')
add('1090', _("Other current assets"), None, DEBIT, 'balance')
# Anlagevermögen
add('11', _("Non-current assets"), None, DEBIT, 'balance')

add('2', _("Passiva"), 'passiva', CREDIT, 'balance')
# Fremdkapital
add('20', _("Liabilities"), 'liabilities', CREDIT, 'balance')
add('2000', _("Suppliers payable"), 'suppliers', CREDIT, 'balance')
add('2010', _("Taxes payable"), 'taxes', CREDIT, 'balance')
add('2020', _("Banks"), 'banks', CREDIT, 'balance')
add('2030', _("Current transfers"), 'transfers', CREDIT, 'balance')
add('2090', _("Other liabilities"), 'other', CREDIT, 'balance')
# Eigenkapital
add('21', _("Own capital"), 'capital', CREDIT, 'balance')
add('2150', _("Net income (loss)"), 'net_income_loss', CREDIT, 'balance')


add('6', _("Expenses"), 'expenses', DEBIT, 'results')
add('6000', _("Cost of sales"), 'costofsales', DEBIT, 'results')
add('6100', _("Operating expenses"), 'operating', DEBIT, 'results')
add('6200', _("Other expenses"), 'otherexpenses', DEBIT, 'results')
add('6900', _("Net income"), 'net_income', DEBIT, 'results')
add('7', _("Revenues"), 'revenues', CREDIT, 'results')
add('7000', _("Net sales"), 'sales', CREDIT, 'results')
add('7900', _("Net loss"), 'net_loss', CREDIT, 'results')


mirror('1010', '2010')
mirror('1020', '2020')
mirror('1030', '2030')
mirror('1090', '2090')
mirror('6900', '7900')



