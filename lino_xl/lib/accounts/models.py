# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from lino import mixins

# from lino.core.roles import SiteStaff
from lino_xl.lib.ledger.roles import LedgerStaff

from .choicelists import CommonAccounts
from .utils import DEBIT, CREDIT, DCLABELS, ZERO


class Group(mixins.BabelNamed):
    class Meta:
        verbose_name = _("Account Group")
        verbose_name_plural = _("Account Groups")

    # ref = dd.NullCharField(
    #     max_length=settings.SITE.plugins.accounts.ref_length, unique=True)
    ref = models.CharField(
        max_length=settings.SITE.plugins.accounts.ref_length,
        blank=True, null=True, unique=True)
    account_type = CommonAccounts.field(blank=True)
    # help_text = dd.RichTextField(_("Introduction"),format="html",blank=True)


class Groups(dd.Table):
    model = 'accounts.Group'
    required_roles = dd.login_required(LedgerStaff)
    order_by = ['ref']
    column_names = 'ref name account_type *'

    insert_layout = """
    name
    account_type ref
    """

    detail_layout = """
    ref name
    account_type id
    #help_text
    AccountsByGroup
    """


@dd.python_2_unicode_compatible
class Account(mixins.BabelNamed, mixins.Sequenced, mixins.Referrable):
    ref_max_length = settings.SITE.plugins.accounts.ref_length

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['ref']

    group = models.ForeignKey('accounts.Group', blank=True, null=True)
    type = CommonAccounts.field()  # blank=True)
    needs_partner = models.BooleanField(_("Needs partner"), default=False)
    clearable = models.BooleanField(_("Clearable"), default=False)
    # default_dc = DebitOrCreditField(_("Default booking direction"))
    default_amount = dd.PriceField(
        _("Default amount"), blank=True, null=True)

    def full_clean(self, *args, **kw):
        if self.group_id is not None:
            if not self.ref:
                qs = rt.modules.accounts.Account.objects.all()
                self.ref = str(qs.count() + 1)
            if not self.name:
                self.name = self.group.name
            self.type = self.group.account_type

        # if self.default_dc is None:
        #     self.default_dc = self.type.dc
        super(Account, self).full_clean(*args, **kw)

    def __str__(self):
        return "(%(ref)s) %(title)s" % dict(
            ref=self.ref,
            title=settings.SITE.babelattr(self, 'name'))


class Accounts(dd.Table):
    model = 'accounts.Account'
    required_roles = dd.login_required(LedgerStaff)
    order_by = ['ref']
    column_names = "ref name group *"
    insert_layout = """
    ref group type
    name
    """
    detail_layout = """
    ref group type id
    name
    needs_partner:30 clearable:30 default_amount:10 #default_dc
    ledger.MovementsByAccount
    """


class AccountsByGroup(Accounts):
    required_roles = dd.login_required()
    master_key = 'group'
    column_names = "ref name *"



