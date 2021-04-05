# -*- coding: UTF-8 -*-
# Copyright 2018-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models

from lino.api import dd, rt, _
from lino_xl.lib.ledger.roles import LedgerStaff
from lino_xl.lib.ledger.choicelists import DC

ref_max_length = dd.plugins.sheets.item_ref_width


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
    verbose_name_plural = _("Common sheet items")
    item_class = CommonItem
    column_names = 'value name text sheet_type dc db_object mirror_ref'
    required_roles = dd.login_required(LedgerStaff)

    @dd.virtualfield(models.CharField(_("Sheet type"), max_length=20))
    def sheet_type(cls, choice, ar):
        return choice.sheet_type

    @dd.virtualfield(models.CharField(_("Mirror"), max_length=20))
    def mirror_ref(cls, choice, ar):
        return choice.mirror_ref

    @dd.virtualfield(DC.field(_("D/C")))
    def dc(cls, choice, ar):
        return choice.dc

    @dd.virtualfield(dd.ForeignKey('sheets.Item'))
    def db_object(cls, choice, ar):
        return choice.get_object()


def mirror(a, b):
    a = CommonItems.get_by_value(a)
    b = CommonItems.get_by_value(b)
    if a.dc != b.dc.opposite():
        raise Exception("Mirroring items must have opposite D/C")
    for i in (a, b):
        if len(i.value) != ref_max_length:
            raise Exception("Cannot mirror non-leaf item {}".format(i))
    a.mirror_ref = b.value
    b.mirror_ref = a.value

add = CommonItems.add_item

# Aktiva (Vermögen)
add('1', _("Assets"), 'assets', DC.debit, 'balance')
# Umlaufvermögen
add('10', _("Current assets"), None, DC.debit, 'balance')
add('1000', _("Customers receivable"), 'customers', DC.debit, 'balance')
add('1010', _("Taxes receivable"), None, DC.debit, 'balance')
add('1020', _("Cash and cash equivalents"), None, DC.debit, 'balance')
add('1030', _("Current transfers"), None, DC.debit, 'balance')
add('1090', _("Other current assets"), None, DC.debit, 'balance')
# Anlagevermögen
add('11', _("Non-current assets"), None, DC.debit, 'balance')

add('2', _("Passiva"), 'passiva', DC.credit, 'balance')
# Fremdkapital
add('20', _("Liabilities"), 'liabilities', DC.credit, 'balance')
add('2000', _("Suppliers payable"), 'suppliers', DC.credit, 'balance')
add('2010', _("Taxes payable"), 'taxes', DC.credit, 'balance')
add('2020', _("Banks"), 'banks', DC.credit, 'balance')
add('2030', _("Current transfers"), 'transfers', DC.credit, 'balance')
add('2090', _("Other liabilities"), 'other', DC.credit, 'balance')
# Eigenkapital
add('21', _("Own capital"), 'capital', DC.credit, 'balance')
add('2150', _("Net income (loss)"), 'net_income_loss', DC.credit, 'balance')

add('4', _("Commercial assets & liabilities"), 'com_ass_lia', DC.credit, 'balance')
add('5', _("Financial assets & liabilities"), 'fin_ass_lia', DC.credit, 'balance')

add('6', _("Expenses"), 'expenses', DC.debit, 'results')
add('60', _("Operation costs"), 'op_costs', DC.debit, 'results')
add('6000', _("Cost of sales"), 'costofsales', DC.debit, 'results')
add('6010', _("Operating expenses"), 'operating', DC.debit, 'results')
add('6020', _("Other expenses"), 'otherexpenses', DC.debit, 'results')
add('62', _("Wages"), 'wages', DC.debit, 'results')
add('6900', _("Net income"), 'net_income', DC.debit, 'results')
add('7', _("Revenues"), 'revenues', DC.credit, 'results')
add('7000', _("Net sales"), 'sales', DC.credit, 'results')
add('7900', _("Net loss"), 'net_loss', DC.credit, 'results')

mirror('1010', '2010')
mirror('1020', '2020')
mirror('1030', '2030')
mirror('1090', '2090')
mirror('6900', '7900')
