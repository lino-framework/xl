# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals


from django.db import models
from lino.api import dd, rt, _

# from .fields import DebitOrCreditField
# from .utils import DEBIT, CREDIT
from lino_xl.lib.ledger.roles import LedgerStaff

class CommonAccount(dd.Choice):
    show_values = True
    clearable = False
    needs_partner = False
    # sheet_item = ''  # filled by lino_xl.lib.sheets if installed
    _instance = None
    
    def __init__(self, value, text, name, clearable, **kwargs):
        # the class attribute `name` ís used as value
        super(CommonAccount, self).__init__(value, text, name, **kwargs)
        # self.sheet_item = CommonItems.get_by_name(actype)
        # self.clearable = clearable
        self.clearable = clearable
        self.needs_partner = clearable

    def create_object(self, **kwargs):
        kwargs.update(dd.str2kw('name', self.text))
        kwargs.update(clearable=self.clearable)
        kwargs.update(needs_partner=self.needs_partner)
        kwargs.update(common_account=self)
        # if dd.is_installed('sheets'):
        #     kwargs.update(sheet_item=self.sheet_item.get_object())
        # else:
        #     kwargs.pop('sheet_item', None)
        return rt.models.accounts.Account(
            ref=self.value, **kwargs)
    
    def get_object(self):
        # return rt.models.accounts.Account.objects.get(ref=self.value)
        if self._instance is None:
            Account = rt.models.accounts.Account
            try:
                self._instance = Account.objects.get(common_account=self)
            except Account.DoesNotExist:
                return None
        return self._instance


class CommonAccounts(dd.ChoiceList):
    verbose_name = _("Common account")
    verbose_name_plural = _("Common accounts")
    item_class = CommonAccount
    column_names = 'value name text clearable db_object'
    required_roles = dd.login_required(LedgerStaff)

    # @dd.virtualfield(models.CharField(_("Sheet item"), max_length=20))
    # def sheet_item(cls, choice, ar):
    #     return choice.sheet_item

    @dd.virtualfield(dd.ForeignKey('accounts.Account'))
    def db_object(cls, choice, ar):
        return choice.get_object()

    @dd.virtualfield(models.BooleanField(_("Clearable")))
    def clearable(cls, choice, ar):
        return choice.clearable


add = CommonAccounts.add_item

add('1000', _("Net income (loss)"),   'net_income_loss', True)
add('4000', _("Customers"),   'customers', True)
add('4300', _("Pending Payment Orders"), 'pending_po', True)
add('4400', _("Suppliers"),   'suppliers', True)
add('4500', _("Employees"),   'employees', True)
add('4600', _("Tax Offices"), 'tax_offices', True)

add('4510', _("VAT due"), 'vat_due', False)
add('4511', _("VAT returnable"), 'vat_returnable', False)
add('4512', _("VAT deductible"), 'vat_deductible', False)
add('4513', _("VAT declared"), 'due_taxes', False)

add('4900', _("Waiting account"), 'waiting', True)

add('5500', _("BestBank"), 'best_bank', False)
add('5700', _("Cash"), 'cash', False)

add('6040', _("Purchase of goods"), 'purchase_of_goods', False)
add('6010', _("Purchase of services"), 'purchase_of_services', False)
add('6020', _("Purchase of investments"), 'purchase_of_investments', False)

add('6300', _("Wages"), 'wages', False)
add('6900', _("Net income"), 'net_income', False)

add('7000', _("Sales"), 'sales', False)
add('7900', _("Net loss"), 'net_loss', False)


# class BankAccounts(Assets):
#     value = '55'
#     text = _("Bank accounts")
#     name = 'bank_accounts'
#     #~ dc = CREDIT
# add(BankAccounts())

