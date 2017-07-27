# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)


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
        # does nothing but we need it so that subclasses like
        # BankAccount can call super().partner_changed()
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
            self.due_date = self.payment_term.get_due_date(self.entry_date)


class Matching(dd.Model):
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

    def get_match(self):
        return self.match or self.get_default_match()


class VoucherItem(dd.Model):

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


