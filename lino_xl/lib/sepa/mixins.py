# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.db import models
from django.core.exceptions import ValidationError

from lino.api import dd, rt, _
from lino.modlib.checkdata.choicelists import Checker
from lino_xl.lib.ledger.utils import DEBIT
from lino_xl.lib.ledger.choicelists import TradeTypes
# from lino_xl.lib.ledger.utils import myround

from lino_xl.lib.ledger.mixins import PartnerRelated


class BankAccount(dd.Model):
    class Meta:
        abstract = True

    bank_account = dd.ForeignKey('sepa.Account', blank=True, null=True)

    def full_clean(self):
        if not self.bank_account:
            self.partner_changed(None)

        super(BankAccount, self).full_clean()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(BankAccount, cls).get_registrable_fields(site):
            yield f
        yield 'bank_account'

    def partner_changed(self, ar):
        # dd.logger.info("20160329 BankAccount.partner_changed")
        Account = rt.models.sepa.Account
        qs = Account.objects.filter(partner=self.get_partner(), primary=True)
        if qs.count() == 1:
            self.bank_account = qs[0]
        else:
            qs = Account.objects.filter(partner=self.get_partner())
            if qs.count() == 1:
                self.bank_account = qs[0]
            else:
                self.bank_account = None
        super(BankAccount, self).partner_changed(ar)

    @dd.chooser()
    def bank_account_choices(cls, partner, project):
        # dd.logger.info(
        #     "20160329 bank_account_choices %s, %s", partner, project)
        partner = partner or project
        return rt.models.sepa.Account.objects.filter(
            partner=partner).order_by('iban')

    def get_bank_account(self):
        """Implements
        :meth:`Voucher.get_bank_account<lino_xl.lib.ledger.models.Voucher.get_bank_account>`.

        """
        return self.bank_account


class BankAccountChecker(Checker):
    """Checks for the following data problems:

    - :message:`Bank account owner ({0}) differs from partner ({1})` --

    """
    verbose_name = _("Check for partner mismatches in bank accounts")
    model = BankAccount
    messages = dict(
        partners_differ=_(
            "Bank account owner ({0}) differs from partner ({1})"),
    )

    def get_checkdata_problems(self, obj, fix=False):

        if obj.bank_account:
            if obj.bank_account.partner != obj.get_partner():

                yield (False, self.messages['partners_differ'].format(
                    obj.bank_account.partner, obj.get_partner()))

BankAccountChecker.activate()
