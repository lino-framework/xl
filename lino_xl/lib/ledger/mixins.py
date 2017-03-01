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


"""Model mixins for `lino_xl.lib.ledger`.

.. autosummary::

"""

from __future__ import unicode_literals

from django.db import models

from lino.api import dd, rt, _
from lino.mixins import Sequenced
# from lino.utils.xmlgen.html import E
# from lino.modlib.notify.utils import rich_text_to_elems

# FKMATCH = False

if dd.is_installed('ledger'):
    project_model = dd.plugins.ledger.project_model
else:
    project_model = None
    

class ProjectRelated(dd.Model):
    """Model mixin for objects that are related to a :attr:`project`.

    .. attribute:: project

        Pointer to the "project". This field exists only if the
        :attr:`project_model
        <lino_xl.lib.ledger.Plugin.project_model>` setting of the
        :mod:`lino_xl.lib.ledger` plugin is nonempty.

    """
    class Meta:
        abstract = True

    project = dd.ForeignKey(
        project_model,
        blank=True, null=True,
        related_name="%(app_label)s_%(class)s_set_by_project")

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(ProjectRelated, cls).get_registrable_fields(site):
            yield f
        if project_model:
            yield 'project'


class PartnerRelated(dd.Model):
    """Base class for things that are related to one and only one trade
    partner. This is base class for both (1) trade document vouchers
    (e.g. invoices or offers) and (2) for the individual entries of
    financial vouchers and ledger movements.

    .. attribute:: partner

        The recipient of this document. A pointer to
        :class:`lino_xl.lib.contacts.models.Partner`.

    .. attribute:: payment_term

        The payment terms to be used in this document.  A pointer to
        :class:`PaymentTerm`.

    .. attribute:: recipient

        Alias for the partner

    """
    class Meta:
        abstract = True

    partner = dd.ForeignKey(
        'contacts.Partner',
        related_name="%(app_label)s_%(class)s_set_by_partner",
        blank=True, null=True)
    payment_term = dd.ForeignKey(
        'ledger.PaymentTerm',
        related_name="%(app_label)s_%(class)s_set_by_payment_term",
        blank=True, null=True)

    def get_partner(self):
        """Overrides Voucher.get_partner"""
        return self.partner

    def get_recipient(self):
        return self.partner
    recipient = property(get_recipient)

    def partner_changed(self, ar):
        # does nothing but we need it so that BankAccount can call
        # super().parnter_changes()
        pass

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(PartnerRelated, cls).get_registrable_fields(site):
            yield f
        yield 'partner'
        yield 'payment_term'

    def full_clean(self, *args, **kw):
        self.fill_defaults()
        super(PartnerRelated, self).full_clean(*args, **kw)

    def fill_defaults(self):
        if not self.payment_term and self.partner_id:
            self.payment_term = self.partner.payment_term
            if self.payment_term:
                self.payment_term_changed()

    def payment_term_changed(self, ar=None):
        if self.payment_term:
            self.due_date = self.payment_term.get_due_date(self.voucher_date)


class Matching(dd.Model):
    """Model mixin for database objects that are considered *matching
    transactions*.  A **matching transaction** is a transaction that
    points to some other movement which it "clears" at least partially.

    A movement is cleared when its amount equals the sum of all
    matching movements.

    Adds a field :attr:`match` and a chooser for it.  Requires a field
    `partner`.  The default implementation of the chooser for
    :attr:`match` requires a `journal`.

    Base class for :class:`lino_xl.lib.vat.AccountInvoice`
    (and e.g. `lino_xl.lib.sales.Invoice`, `lino_xl.lib.finan.DocItem`)
    
    .. attribute:: match

       Pointer to the :class:`movement
       <lino.modlib.ledger.models.Movement>` which is being cleared by
       this movement.

    """
    class Meta:
        abstract = True

    match = dd.CharField(
        _("Match"), max_length=20, blank=True,
        help_text=_("The movement to be matched."))

    @classmethod
    def get_match_choices(cls, journal, partner):
        """This is the general algorithm.
        """
        matchable_accounts = rt.modules.accounts.Account.objects.filter(
            matchrule__journal=journal)
        fkw = dict(account__in=matchable_accounts)
        fkw.update(cleared=False)
        if partner:
            fkw.update(partner=partner)
        qs = rt.modules.ledger.Movement.objects.filter(**fkw)
        qs = qs.order_by('value_date')
        # qs = qs.distinct('match')
        return qs.values_list('match', flat=True)

    @dd.chooser(simple_values=True)
    def match_choices(cls, journal, partner):
        # todo: move this to implementing classes?
        return cls.get_match_choices(journal, partner)


class VoucherItem(dd.Model):
    """Base class for items of a voucher.

    Subclasses must define the following fields:

    .. attribute:: voucher

        Pointer to the voucher which contains this item.  Non
        nullable.  The voucher must be a subclass of
        :class:`ledger.Voucher<lino_xl.lib.ledger.models.Voucher>`.
        The `related_name` must be `'items'`.
    

    .. attribute:: title

        The title of this voucher.

        Currently (because of :djangoticket:`19465`), this field is
        not implemented here but in the subclasses:

        :class:`lino_xl.lib.vat.models.AccountInvoice`
        :class:`lino_xl.lib.vat.models.InvoiceItem`

    """

    allow_cascaded_delete = ['voucher']

    class Meta:
        abstract = True

    # title = models.CharField(_("Description"), max_length=200, blank=True)

    def get_row_permission(self, ar, state, ba):
        """Items of registered invoices may not be edited

        """
        if not self.voucher.state.editable:
            if not ba.action.readonly:
                return False
        return super(VoucherItem, self).get_row_permission(ar, state, ba)


class SequencedVoucherItem(Sequenced):

    class Meta:
        abstract = True

    def get_siblings(self):
        return self.voucher.items.all()


class AccountVoucherItem(VoucherItem, SequencedVoucherItem):
    """Abstract base class for voucher items which point to an account.
    This is subclassed by
    :class:`lino_xl.lib.vat.models.InvoiceItem`
    and
    :class:`lino_xl.lib.vatless.models.InvoiceItem`.
    It defines the :attr:`account` field and some related methods.

    .. attribute:: account

        ForeignKey pointing to the account (:class:`accounts.Account
        <lino_xl.lib.accounts.models.Account>`) that is to be moved.

    """

    class Meta:
        abstract = True

    account = models.ForeignKey(
        'accounts.Account',
        related_name="%(app_label)s_%(class)s_set_by_account")

    def get_base_account(self, tt):
        return self.account

    @dd.chooser()
    def account_choices(self, voucher):
        if voucher and voucher.journal:
            fkw = {voucher.journal.trade_type.name + '_allowed': True}
            return rt.modules.accounts.Account.objects.filter(**fkw)
        return []


def JournalRef(**kw):
    # ~ kw.update(blank=True,null=True) # Django Ticket #12708
    kw.update(related_name="%(app_label)s_%(class)s_set_by_journal")
    return dd.ForeignKey('ledger.Journal', **kw)


def VoucherNumber(*args, **kwargs):
    return models.IntegerField(*args, **kwargs)


