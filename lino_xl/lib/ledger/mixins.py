# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from builtins import str

from django.db import models

from lino.api import dd, rt, _
from lino.mixins import Sequenced

from etgen.html import E

from .choicelists import VoucherTypes
from .roles import LedgerUser

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

    def get_print_language(self):
        p = self.get_partner()
        if p is not None:
            return p.language

    def get_recipient(self):
        return self.partner
    recipient = property(get_recipient)

    def partner_changed(self, ar=None):
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
        matchable_accounts = rt.models.ledger.Account.objects.filter(
            matchrule__journal=journal)
        fkw = dict(account__in=matchable_accounts)
        fkw.update(cleared=False)
        if partner:
            fkw.update(partner=partner)
        qs = rt.models.ledger.Movement.objects.filter(**fkw)
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
        if not self.voucher.state.is_editable:
            if not ba.action.readonly:
                return False
        return super(VoucherItem, self).get_row_permission(ar, state, ba)

    def get_ana_account(self):
        return None

class SequencedVoucherItem(Sequenced):

    class Meta:
        abstract = True

    def get_siblings(self):
        return self.voucher.items.all()


class AccountVoucherItem(VoucherItem, SequencedVoucherItem):

    class Meta:
        abstract = True

    account = dd.ForeignKey(
        'ledger.Account',
        related_name="%(app_label)s_%(class)s_set_by_account")

    def get_base_account(self, tt):
        return self.account

    @dd.chooser()
    def account_choices(self, voucher):
        if voucher and voucher.journal:
            return voucher.journal.get_allowed_accounts()
        return rt.models.ledger.Account.objects.none()


# def set_partner_invoice_account(sender, instance=None, **kwargs):
#     if instance.account:
#         return
#     if not instance.voucher:
#         return
#     p = instance.voucher.partner
#     if not p:
#         return
#     tt = instance.voucher.get_trade_type()
#     instance.account = tt.get_partner_invoice_account(p)

# @dd.receiver(dd.post_analyze)
# def on_post_analyze(sender, **kw):
#     for m in rt.models_by_base(AccountVoucherItem):
#         dd.post_init.connect(set_partner_invoice_account, sender=m)
    


def JournalRef(**kw):
    # ~ kw.update(blank=True,null=True) # Django Ticket #12708
    kw.update(related_name="%(app_label)s_%(class)s_set_by_journal")
    return dd.ForeignKey('ledger.Journal', **kw)


def VoucherNumber(*args, **kwargs):
    return models.IntegerField(*args, **kwargs)


class PeriodRange(dd.Model):
    class Meta:
        abstract = True

    start_period = dd.ForeignKey(
        'ledger.AccountingPeriod',
        blank=True, verbose_name=_("Start period"),
        related_name="%(app_label)s_%(class)s_set_by_start_period")

    end_period = dd.ForeignKey(
        'ledger.AccountingPeriod',
        blank=True, null=True,
        verbose_name=_("End period"),
        related_name="%(app_label)s_%(class)s_set_by_end_period")

    
    def get_period_filter(self, fieldname, **kwargs):
        return rt.models.ledger.AccountingPeriod.get_period_filter(
            fieldname, self.start_period, self.end_period, **kwargs)
    
    
class PeriodRangeObservable(dd.Model):
    class Meta:
        abstract = True
        
    observable_period_field = 'accounting_period'


    @classmethod
    def setup_parameters(cls, fields):
        fields.update(
            start_period=dd.ForeignKey(
                'ledger.AccountingPeriod',
                blank=True, null=True,
                help_text=_("Start of observed period range"),
                verbose_name=_("Period from")))
        fields.update(
            end_period=dd.ForeignKey(
                'ledger.AccountingPeriod',
                blank=True, null=True,
                help_text=_(
                    "Optional end of observed period range. "
                    "Leave empty to consider only the Start period."),
                verbose_name=_("Period until")))
        super(PeriodRangeObservable, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        pv = ar.param_values
        qs = super(PeriodRangeObservable, cls).get_request_queryset(ar, **kwargs)
        flt = rt.models.ledger.AccountingPeriod.get_period_filter(
            cls.observable_period_field, pv.start_period, pv.end_period)
        return qs.filter(**flt)

    @classmethod
    def get_title_tags(cls, ar):
        for t in super(PeriodRangeObservable, cls).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.start_period is not None:
            if pv.end_period is None:
                yield str(pv.start_period)
            else:
                yield "{}..{}".format(pv.start_period, pv.end_period)

                
class ItemsByVoucher(dd.Table):
    label = _("Content")
    required_roles = dd.login_required(LedgerUser)
    master_key = 'voucher'
    order_by = ["seqno"]
    auto_fit_column_widths = True
    display_mode = 'html'
    preview_limit = 0

class VouchersByPartnerBase(dd.VirtualTable):
    """Shows all ledger vouchers of a given partner.
    
    This is a :class:`lino.core.tables.VirtualTable` with a customized
    slave summary.

    """
    label = _("Partner vouchers")
    required_roles = dd.login_required(LedgerUser)

    order_by = ["-entry_date", '-id']
    master = 'contacts.Partner'
    display_mode = 'summary'

    _master_field_name = 'partner'
    _voucher_base = PartnerRelated

    @classmethod
    def get_data_rows(self, ar):
        obj = ar.master_instance
        rows = []
        if obj is not None:
            flt = {self._master_field_name: obj}
            for M in rt.models_by_base(self._voucher_base):
                rows += list(M.objects.filter(**flt))

            # def by_date(a, b):
            #     return cmp(b.entry_date, a.entry_date)

            rows.sort(key= lambda i: i.entry_date)
        return rows

    @dd.displayfield(_("Voucher"))
    def voucher(self, row, ar):
        return ar.obj2html(row)

    @dd.virtualfield('ledger.Movement.partner')
    def partner(self, row, ar):
        return row.partner

    @dd.virtualfield('ledger.Voucher.entry_date')
    def entry_date(self, row, ar):
        return row.entry_date

    @dd.virtualfield('ledger.Voucher.state')
    def state(self, row, ar):
        return row.state

    @classmethod
    def get_table_summary(self, obj, ar):

        elems = []
        sar = self.request(master_instance=obj)
        # elems += ["Partner:", unicode(ar.master_instance)]
        for voucher in sar:
            vc = voucher.get_mti_leaf()
            if vc and vc.state.name == "draft":
                elems += [ar.obj2html(vc), " "]

        vtypes = []
        for vt in VoucherTypes.items():
            if issubclass(vt.model, self._voucher_base):
                vtypes.append(vt)

        actions = []

        def add_action(btn):
            if btn is None:
                return False
            actions.append(btn)
            return True

        if not ar.get_user().user_type.readonly:
            flt = {self._master_field_name: obj}
            for vt in vtypes:
                for jnl in vt.get_journals():
                    sar = vt.table_class.insert_action.request_from(
                        ar, master_instance=jnl,
                        known_values=flt)
                    btn = sar.ar2button(label=str(jnl), icon_name=None)
                    if len(actions):
                        actions.append(', ')
                    actions.append(btn)

            elems += [E.br(), str(_("Create voucher in journal")), " "] + actions
        return E.div(*elems)
