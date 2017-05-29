# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals


from django.db import models
from lino.api import dd, _

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
        return [o for o in AccountTypes.objects()
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


class AccountType(dd.Choice):
    top_level = True
    sheet = None
    #~ def __init__(self,value,text,name,dc=True,**kw):
        #~ self.dc = dc
        #~ super(AccountType,self).__init__(value,text,name)

    def __init__(self):
        pass
        #~ self.dc = dc
        #~ super(AccountType,self).__init__(value,text,name)


class Assets(AccountType):
    value = 'A'
    text = _("Assets")   # Aktiva, Anleihe, Vermögen, Anlage
    name = "assets"
    dc = DEBIT
    sheet = BalanceSheet


class Liabilities(AccountType):
    value = 'L'
    text = _("Liabilities")  # Guthaben, Schulden, Verbindlichkeit
    name = "liabilities"
    dc = CREDIT
    sheet = BalanceSheet


class Capital(AccountType):  # aka Owner's Equities
    value = 'C'
    text = _("Capital")  # Kapital
    name = "capital"
    dc = CREDIT
    sheet = BalanceSheet


class Income(AccountType):
    value = 'I'
    text = _("Incomes")  # Gain/Revenue     Einnahmen  Produits
    name = "incomes"
    dc = CREDIT
    balance_sheet = True
    sheet = EarningsSheet


class Expenses(AccountType):
    value = 'E'
    text = _("Expenses")  # Loss/Cost       Ausgaben   Charges
    name = "expenses"
    dc = DEBIT
    sheet = EarningsSheet


class BankAccounts(Assets):
    top_level = False
    value = 'B'
    text = _("Bank accounts")
    name = 'bank_accounts'
    #~ dc = CREDIT


class AccountTypes(dd.ChoiceList):
    verbose_name = _("Account Type")
    item_class = AccountType
    column_names = 'value name text dc sheet'

    @dd.virtualfield(DebitOrCreditField(_("D/C")))
    def dc(cls, choice, ar):
        return choice.dc

    @dd.virtualfield(models.CharField(_("Sheet"), max_length=20))
    def sheet(cls, choice, ar):
        return choice.sheet.__name__


add = AccountTypes.add_item
add = AccountTypes.add_item_instance
add(Assets())
add(Liabilities())
add(Income())
add(Expenses())
add(Capital())
add(BankAccounts())


