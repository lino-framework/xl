# -*- coding: UTF-8 -*-
# Copyright 2008-2016 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""Database models for `lino_xl.lib.accounts`.

"""

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from lino import mixins

# from lino.core.roles import SiteStaff
from lino_xl.lib.ledger.roles import LedgerStaff

from .choicelists import *
from .utils import DEBIT, CREDIT, DCLABELS, ZERO


class Group(mixins.BabelNamed):
    "A group of accounts."
    class Meta:
        verbose_name = _("Account Group")
        verbose_name_plural = _("Account Groups")

    ref = dd.NullCharField(
        max_length=settings.SITE.plugins.accounts.ref_length, unique=True)
    account_type = AccountTypes.field(blank=True)
    # help_text = dd.RichTextField(_("Introduction"),format="html",blank=True)


class Groups(dd.Table):
    """The global table of all account groups."""
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
    """An **account** is an item of an account chart used to collect
    ledger transactions or other accountable items.

    .. attribute:: name

        The multilingual designation of this account, as the users see
        it.


    .. attribute:: group

        The *account group* to which this account belongs.  Points to
        an instance of :class:`Group`.  If this field is empty, the
        account won't appear in certain reports.
    
    .. attribute:: seqno

        The sequence number of this account within its :attr:`group`.
    
    .. attribute:: ref

        An optional unique name which can be used to reference a given
        account.

    .. attribute:: type

        The *account type* of this account.  This points to an item of
        :class:`AccountTypes
        <lino_xl.lib.accounts.choicelists.AccountTypes>`.
    
    .. attribute:: needs_partner

        Whether bookings to this account need a partner specified.

        This causes the contra entry of financial documents to be
        detailed (i.e. one for every item) or not (i.e. a single
        contra entry per voucher, without project nor partner).

    .. attribute:: default_amount

        The default amount to book in bank statements or journal
        entries when this account has been selected manually. The
        default booking direction is that of the :attr:`type`.

    """
    ref_max_length = settings.SITE.plugins.accounts.ref_length

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['ref']

    group = models.ForeignKey('accounts.Group', blank=True, null=True)
    type = AccountTypes.field()  # blank=True)
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



