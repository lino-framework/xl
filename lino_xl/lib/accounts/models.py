# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from lino import mixins

from lino_xl.lib.ledger.roles import LedgerStaff

from .choicelists import CommonAccounts
from .utils import DEBIT, CREDIT, DCLABELS, ZERO


@dd.python_2_unicode_compatible
class Account(mixins.BabelNamed, mixins.Sequenced, mixins.Referrable):
    ref_max_length = settings.SITE.plugins.accounts.ref_length

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['ref']

    sheet_item = dd.ForeignKey('sheets.Item', null=True, blank=True)
    common_account = CommonAccounts.field(blank=True)
    needs_partner = models.BooleanField(_("Needs partner"), default=False)
    clearable = models.BooleanField(_("Clearable"), default=False)
    # default_dc = DebitOrCreditField(_("Default booking direction"))
    default_amount = dd.PriceField(
        _("Default amount"), blank=True, null=True)

    def __str__(self):
        return "(%(ref)s) %(title)s" % dict(
            ref=self.ref,
            title=settings.SITE.babelattr(self, 'name'))
    
    @dd.chooser()
    def sheet_item_choices(cls):
        return rt.models.sheets.Item.get_usable_items()


class Accounts(dd.Table):
    model = 'accounts.Account'
    required_roles = dd.login_required(LedgerStaff)
    order_by = ['ref']
    column_names = "ref name *"
    insert_layout = """
    ref sheet_item
    name
    """
    detail_layout = """
    ref common_account sheet_item id
    name
    needs_partner:30 clearable:30 default_amount:10 #default_dc
    ledger.MovementsByAccount
    """


