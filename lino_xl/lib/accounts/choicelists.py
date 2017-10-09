# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals


from django.db import models
from lino.api import dd, rt, _

from .fields import DebitOrCreditField
from .utils import DEBIT, CREDIT


class Sheet(object):

    # Comptes annuels Jahresabschluss Jaarverslag  Aastaaruanne
    verbose_name = _("Financial statement")

    @classmethod
    def account_types(cls):
        """
        Return a list the top-level account types included in this Sheet
        """
        return [o for o in CommonAccounts.objects()
                if o.sheet == cls and o.top_level]


class BalanceSheet(Sheet):

    verbose_name = _("Balance sheet")  # Bilan  Bilanz  Balans  Bilanss


class EarningsSheet(Sheet):

    # Compte de résultat Gewinn- und Verlustrechnung
    # Winst-en-verliesrekening ...
    verbose_name = _("Profit & Loss statement")


class CashFlowSheet(Sheet):
    verbose_name = _("Cash flow statement")

# La balance des comptes (généraux|particuliers|fournisseurs|clients)


class AccountsBalanceSheet(Sheet):
    verbose_name = _("Accounts balances")


Sheet.objects = (BalanceSheet, EarningsSheet, CashFlowSheet)


class CommonAccount(dd.Choice):
    # top_level = True
    sheet = None
    clearable = False
    needs_partner = False
    
    def __init__(self):
        # the class attribute `name` ís used as value
        super(CommonAccount, self).__init__(
            self.value, self.text, self.name)
        self.top_level = len(self.value) == 1

    def create_object(self, **kwargs):
        kwargs.update(dd.str2kw('name', self.text))
        kwargs.update(clearable=self.clearable)
        kwargs.update(needs_partner=self.needs_partner)
        return rt.models.accounts.Account(
            ref=self.value, type=self,  **kwargs)
    
    def get_object(self):
        # return rt.models.accounts.Account.objects.get(ref=self.value)
        Account = rt.models.accounts.Account
        try:
            return Account.objects.get(ref=self.value)
        except Account.DoesNotExist:
            return None



class CommonAccounts(dd.ChoiceList):
    verbose_name = _("Account Type")
    item_class = CommonAccount
    column_names = 'value name text dc sheet'

    @dd.virtualfield(DebitOrCreditField(_("D/C")))
    def dc(cls, choice, ar):
        return choice.dc

    @dd.virtualfield(models.CharField(_("Sheet"), max_length=20))
    def sheet(cls, choice, ar):
        return choice.sheet.__name__


add = CommonAccounts.add_item_instance

class Assets(CommonAccount):
    value = 'A'
    text = _("Assets")   # Aktiva, Anleihe, Vermögen, Anlage
    name = "assets"
    dc = DEBIT
    sheet = BalanceSheet
add(Assets())


class Liabilities(CommonAccount):
    value = 'L'
    text = _("Liabilities")  # Guthaben, Schulden, Verbindlichkeit
    name = "liabilities"
    dc = CREDIT
    sheet = BalanceSheet
add(Liabilities())


class Capital(CommonAccount):  # aka Owner's Equities
    value = 'C'
    text = _("Capital")  # Kapital
    name = "capital"
    dc = CREDIT
    sheet = BalanceSheet
add(Capital())


class Income(CommonAccount):
    value = 'I'
    text = _("Incomes")  # Gain/Revenue     Einnahmen  Produits
    name = "incomes"
    dc = CREDIT
    balance_sheet = True
    sheet = EarningsSheet
add(Income())


class Expenses(CommonAccount):
    value = 'E'
    text = _("Expenses")  # Loss/Cost       Ausgaben   Charges
    name = "expenses"
    dc = DEBIT
    sheet = EarningsSheet
add(Expenses())


class BankAccounts(Assets):
    value = '55'
    text = _("Bank accounts")
    name = 'bank_accounts'
    #~ dc = CREDIT
add(BankAccounts())



class Customers(Assets):
    value = '4000'
    text = _("Customers")
    name = "customers"
    clearable = True
    needs_partner = True
add(Customers())

class Suppliers(Liabilities):
    value = '4400'
    text = _("Suppliers")
    name = "suppliers"
    clearable=True
    needs_partner=True
add(Suppliers())

class TaxOffices(Liabilities):
    value = '4600'
    text = _("Tax Offices")
    name = 'tax_offices'
    clearable = True
    needs_partner = True
add(TaxOffices())

class Employees(Liabilities):
    value = '4500'
    text = _("Employees")
    name = "employees"
    clearable=True
    needs_partner=True
add(Employees())

class PendingPaymentOrders(Assets):
    value = '4700'
    text = _("Pending Payment Orders")
    name = 'pending_po'
    clearable = True
    needs_partner = True
add(PendingPaymentOrders())


class VatDue(Liabilities):
    value = '4510'
    text = _("VAT due")
    name = 'vat_due'
    clearable = True
    needs_partner = True
add(VatDue())

class VatReturnable(Liabilities):
    value = '4511'
    text = _("VAT returnable")
    name = 'vat_returnable'
add(VatReturnable())

class VatDeductible(Liabilities):
    value = '4512'
    text = _("VAT deductible")
    name = 'vat_deductible'
add(VatDeductible())

class VatDeclared(Liabilities):
    value = '4513'
    text = _("VAT declared")
    name = 'due_taxes'
    clearable=True
    needs_partner=True
add(VatDeclared())

class BestBank(BankAccounts):
    value = '5500'
    text = _("BestBank")
    name = 'best_bank'
add(BestBank())

class Cash(BankAccounts):
    value = '5700'
    text = _("Cash")
    name = 'cash'
add(Cash())

class PurchaseOfGoods(Expenses):
    value = '6040'
    text = _("Purchase of goods")
    name = 'purchase_of_goods'
add(PurchaseOfGoods())

class PurchaseOfServices(Expenses):
    value = '6010'
    text = _("Purchase of services")
    name = 'purchase_of_services'
add(PurchaseOfServices())

class PurchaseOfInvestments(Expenses):
    value = '6020'
    text = _("Purchase of investments")
    name = 'purchase_of_investments'
add(PurchaseOfInvestments())

class Wages(Expenses):
    value = '6300'
    text = _("Wages")
    name = 'wages'
add(Wages())

class Sales(Income):
    value = '7000'
    text = _("Sales")
    name = 'sales'
add(Sales())

# TODO: move the following definition to lino_voga
class MembershipFees(Sales):
    value = '7310'
    text = _("Membership fees")
    name = 'membership_fees'
add(MembershipFees())
