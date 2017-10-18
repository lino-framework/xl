# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals


from django.db import models
from lino.api import dd, rt, _

from .fields import DebitOrCreditField
from .utils import DEBIT, CREDIT
from lino_xl.lib.ledger.roles import LedgerStaff


class Sheet(object):

    # Comptes annuels Jahresabschluss Jaarverslag  Aastaaruanne
    verbose_name = _("Financial statement")

    @classmethod
    def account_types(cls):
        """
        Return a list the top-level account types included in this Sheet
        """
        return [o for o in AccountTypes.objects() if o.sheet == cls]


class BalanceSheet(Sheet):

    verbose_name = _("Balance sheet")  # Bilan  Bilanz  Balans  Bilanss


class EarningsSheet(Sheet):

    # Compte de résultat Gewinn- und Verlustrechnung
    # Winst-en-verliesrekening ...
    verbose_name = _("Profit & Loss statement")


# class CashFlowSheet(Sheet):
#     verbose_name = _("Cash flow statement")

# La balance des comptes (généraux|particuliers|fournisseurs|clients)

# class AccountBalancesSheet(Sheet):
#     verbose_name = _("Account balances")


Sheet.objects = (BalanceSheet, EarningsSheet)


class AccountType(dd.Choice):
    # top_level = True
    sheet = None
    
    def __init__(self, *args, **kwargs):
        # the class attribute `name` ís used as value
        super(AccountType, self).__init__(*args, **kwargs)
        self.top_level = len(self.value) == 1

    

class AccountTypes(dd.ChoiceList):
    verbose_name = _("Account type")
    verbose_name_plural = _("Account types")
    item_class = AccountType
    column_names = 'value name text dc sheet'
    required_roles = dd.login_required(LedgerStaff)
    
    @dd.virtualfield(DebitOrCreditField(_("D/C")))
    def dc(cls, choice, ar):
        return choice.dc

    @dd.virtualfield(models.CharField(_("Sheet"), max_length=20))
    def sheet(cls, choice, ar):
        return choice.sheet.__name__


add = AccountTypes.add_item_instance

class Assets(AccountType):
    value = 'A'
    text = _("Assets")   # Aktiva, Anleihe, Vermögen, Anlage
    name = "assets"
    dc = DEBIT
    sheet = BalanceSheet
add(Assets())


class Liabilities(AccountType):
    value = 'L'
    text = _("Liabilities")  # Guthaben, Schulden, Verbindlichkeit
    name = "liabilities"
    dc = CREDIT
    sheet = BalanceSheet
add(Liabilities())


class Capital(AccountType):  # aka Owner's Equities
    value = 'C'
    text = _("Capital")  # Kapital
    name = "capital"
    dc = CREDIT
    sheet = BalanceSheet
add(Capital())


class Incomes(AccountType):
    value = 'I'
    text = _("Incomes")  # Gain/Revenue     Einnahmen  Produits
    name = "incomes"
    dc = CREDIT
    balance_sheet = True
    sheet = EarningsSheet
add(Incomes())


class Expenses(AccountType):
    value = 'E'
    text = _("Expenses")  # Loss/Cost       Ausgaben   Charges
    name = "expenses"
    dc = DEBIT
    sheet = EarningsSheet
add(Expenses())


class CommonAccount(dd.Choice):
    show_values = True
    clearable = False
    needs_partner = False
    account_type = None
    _instance = None
    
    def __init__(self, value, text, name, actype, clearable, **kwargs):
        # the class attribute `name` ís used as value
        super(CommonAccount, self).__init__(value, text, name, **kwargs)
        self.account_type = AccountTypes.get_by_name(actype)
        self.clearable = clearable
        self.clearable = clearable
        self.needs_partner = clearable

    def create_object(self, **kwargs):
        kwargs.update(dd.str2kw('name', self.text))
        kwargs.update(clearable=self.clearable)
        kwargs.update(needs_partner=self.needs_partner)
        kwargs.update(common_account=self)
        kwargs.update(type=self.account_type)
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
    column_names = 'value name text account_type clearable db_object'
    required_roles = dd.login_required(LedgerStaff)

    @dd.virtualfield(models.CharField(_("Account type"), max_length=20))
    def account_type(cls, choice, ar):
        return choice.account_type

    @dd.virtualfield(dd.ForeignKey('accounts.Account'))
    def db_object(cls, choice, ar):
        return choice.get_object()

    @dd.virtualfield(models.BooleanField(_("Clearable")))
    def clearable(cls, choice, ar):
        return choice.clearable


add = CommonAccounts.add_item

add('4000', _("Customers"),   'customers', 'assets', True)
add('4300', _("Pending Payment Orders"), 'pending_po', 'assets', True)
add('4400', _("Suppliers"),   'suppliers', 'liabilities', True)
add('4500', _("Employees"),   'employees', 'liabilities', True)
add('4600', _("Tax Offices"), 'tax_offices', 'liabilities', True)

add('4510', _("VAT due"), 'vat_due', 'liabilities', False)
add('4511', _("VAT returnable"), 'vat_returnable', 'liabilities', False)
add('4512', _("VAT deductible"), 'vat_deductible', 'liabilities', False)
add('4513', _("VAT declared"), 'due_taxes', 'liabilities', False)

add('5500', _("BestBank"), 'best_bank', 'assets', False)
add('5700', _("Cash"), 'cash', 'assets', False)

add('6040', _("Purchase of goods"), 'purchase_of_goods', 'expenses', False)
add('6010', _("Purchase of services"), 'purchase_of_services', 'expenses', False)
add('6020', _("Purchase of investments"), 'purchase_of_investments', 'expenses', False)

add('6300', _("Wages"), 'wages', 'expenses', False)

add('7000', _("Sales"), 'sales', 'incomes', False)


# class BankAccounts(Assets):
#     value = '55'
#     text = _("Bank accounts")
#     name = 'bank_accounts'
#     #~ dc = CREDIT
# add(BankAccounts())

