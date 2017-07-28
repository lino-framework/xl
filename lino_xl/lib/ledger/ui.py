# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""User interface definitions for this plugin.


"""

from __future__ import unicode_literals
import six

import logging
logger = logging.getLogger(__name__)

from django.db import models

from lino.api import dd, rt, _
from lino import mixins
from lino.utils.report import Report
from lino.utils.xmlgen.html import E
from lino.utils import join_elems

from lino_xl.lib.accounts.utils import DEBIT, CREDIT, ZERO

from .utils import Balance, DueMovement, get_due_movements
from .choicelists import TradeTypes, FiscalYears, VoucherTypes, JournalGroups
from .choicelists import VoucherStates
from .mixins import JournalRef
from .roles import AccountingReader, LedgerUser, LedgerStaff


class JournalDetail(dd.DetailLayout):
    main = """
    name ref:5
    trade_type seqno id voucher_type:10 journal_group:10
    account build_method template
    dc force_sequence #invert_due_dc yearly_numbering auto_check_clearings must_declare
    printed_name
    MatchRulesByJournal
    """


class Journals(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'ledger.Journal'
    order_by = ["seqno"]
    column_names = "ref:5 name trade_type journal_group " \
                   "voucher_type force_sequence * seqno id"
    detail_layout = JournalDetail()
    insert_layout = dd.InsertLayout("""
    ref name
    journal_group
    voucher_type
    """, window_size=(60, 'auto'))

class ByJournal(dd.Table):
    # order_by = ["-entry_date", '-id']
    order_by = ["-accounting_period__year", "-number"]
    master_key = 'journal'
    # start_at_bottom = True
    required_roles = dd.login_required(LedgerUser)
    params_layout = "start_period end_period state user"

    @classmethod
    def get_title_base(self, ar):
        """Without this override we would have a title like "Invoices of
        journal <Invoices>".  But we want just "Invoices".

        """
        return unicode(ar.master_instance)

    @classmethod
    def create_journal(cls, trade_type=None, account=None, **kw):
        vt = VoucherTypes.get_for_table(cls)
        if isinstance(trade_type, six.string_types):
            trade_type = TradeTypes.get_by_name(trade_type)
        if isinstance(account, six.string_types):
            account = rt.modules.accounts.Account.get_by_ref(account)
        if account is not None:
            kw.update(account=account)
        return rt.modules.ledger.Journal(
            trade_type=trade_type, voucher_type=vt, **kw)

class PrintableByJournal(ByJournal):
    editable = False
    params_layout = "journal start_period end_period state"
    
    column_names = "number entry_date partner total_base total_vat total_incl vat_regime *"

    @classmethod
    def setup_request(self, ar):
        ar.master_instance = ar.param_values.journal


class AccountingPeriods(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'ledger.AccountingPeriod'
    order_by = ["ref", "start_date", "year"]
    column_names = "ref start_date end_date year state remark *"


class PaymentTerms(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'ledger.PaymentTerm'
    order_by = ["ref"]
    column_names = "ref name months days end_of_month *"
    detail_layout = """
    ref months days end_of_month
    name
    printed_text
    """


class Vouchers(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = 'ledger.Voucher'
    editable = False
    order_by = ["entry_date", "number"]
    column_names = "entry_date number *"
    parameters = dict(
        year=FiscalYears.field(blank=True),
        journal=JournalRef(blank=True))
    params_layout = "journal start_period end_period state user"

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(Vouchers, cls).get_request_queryset(ar)
        if isinstance(qs, list):
            return qs
        pv = ar.param_values
        if pv.year:
            qs = qs.filter(accounting_period__year=pv.year)
        if pv.journal:
            qs = qs.filter(journal=pv.journal)
        return qs


class AllVouchers(Vouchers):
    required_roles = dd.login_required(LedgerStaff)


class MatchRules(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'ledger.MatchRule'


class MatchRulesByAccount(MatchRules):
    master_key = 'account'
    column_names = "journal *"


class MatchRulesByJournal(ByJournal, MatchRules):
    order_by = ["account"]
    master_key = 'journal'
    column_names = "account *"
    params_layout = None


class ExpectedMovements(dd.VirtualTable):
    row_height = 4
    required_roles = dd.login_required(AccountingReader)
    label = _("Debts")
    icon_name = 'book_link'
    #~ column_names = 'match due_date debts payments balance'
    column_names = 'due_date:15 balance debts payments'
    auto_fit_column_widths = True
    # variable_row_height = True
    parameters = dd.ParameterPanel(
        date_until=models.DateField(_("Date until"), blank=True, null=True),
        trade_type=TradeTypes.field(blank=True),
        from_journal=dd.ForeignKey('ledger.Journal', blank=True),
        for_journal=dd.ForeignKey(
            'ledger.Journal', blank=True, verbose_name=_("Clearable by")),
        account=dd.ForeignKey('accounts.Account', blank=True),
        partner=dd.ForeignKey('contacts.Partner', blank=True),
        project=dd.ForeignKey(dd.plugins.ledger.project_model, blank=True),
        show_sepa=dd.YesNo.field(blank=True),
    )
    params_layout = "trade_type date_until from_journal " \
                    "for_journal project partner account show_sepa"

    @classmethod
    def get_dc(cls, ar=None):
        return DEBIT

    @classmethod
    def get_data_rows(cls, ar, **flt):
        #~ if ar.param_values.journal:
            #~ pass
        pv = ar.param_values
        # if pv is None:
        #     raise Exception("No pv in %s" % ar)
        if pv.trade_type:
            flt.update(account=pv.trade_type.get_partner_account())
        if pv.partner:
            flt.update(partner=pv.partner)
        if pv.account:
            flt.update(account=pv.account)
        if pv.project:
            flt.update(project=pv.project)
        if pv.show_sepa == dd.YesNo.yes:
            flt.update(partner__sepa_accounts__primary=True)
        elif pv.show_sepa == dd.YesNo.no:
            flt.update(partner__sepa_accounts__primary__isnull=True)
        if pv.date_until is not None:
            flt.update(value_date__lte=pv.date_until)
        if pv.for_journal is not None:
            accounts = rt.modules.accounts.Account.objects.filter(
                matchrule__journal=pv.for_journal).distinct()
            flt.update(account__in=accounts)
        if pv.from_journal is not None:
            flt.update(voucher__journal=pv.from_journal)
        return get_due_movements(cls.get_dc(ar), **flt)

    @classmethod
    def get_pk_field(self):
        return rt.modules.ledger.Movement._meta.pk

    @classmethod
    def get_row_by_pk(cls, ar, pk):
        # for i in ar.data_iterator:
        #     if i.id == pk:
        #         return i
        # raise Exception("Not found: %s in %s" % (pk, ar))
        mvt = rt.modules.ledger.Movement.objects.get(pk=pk)
        dm = DueMovement(cls.get_dc(ar), mvt)
        dm.collect_all()
        return dm

    @dd.displayfield(_("Info"))
    def info(self, row, ar):
        elems = []
        if row.project:
            elems.append(ar.obj2html(row.project))
        if row.partner:
            elems.append(ar.obj2html(row.partner))
            # elems.append(row.partner.address)
        if row.bank_account:
            elems.append(ar.obj2html(row.bank_account))
        if row.account:
            elems.append(ar.obj2html(row.account))
        # return E.span(*join_elems(elems, ' / '))
        return E.span(*join_elems(elems, E.br))
        # return E.span(*elems)

    @dd.displayfield(_("Match"))
    def match(self, row, ar):
        return row.match

    @dd.virtualfield(
        models.DateField(
            _("Due date"),
            help_text=_("Due date of the eldest debt in this match group")))
    def due_date(self, row, ar):
        return row.due_date

    @dd.displayfield(
        _("Debts"), help_text=_("List of invoices in this match group"))
    def debts(self, row, ar):
        return E.span(*join_elems([   # E.p(...) until 20150128
            ar.obj2html(i.voucher.get_mti_leaf()) for i in row.debts]))

    @dd.displayfield(
        _("Payments"), help_text=_("List of payments in this match group"))
    def payments(self, row, ar):
        return E.span(*join_elems([    # E.p(...) until 20150128
            ar.obj2html(i.voucher.get_mti_leaf()) for i in row.payments]))

    @dd.virtualfield(dd.PriceField(_("Balance")))
    def balance(self, row, ar):
        return row.balance

    @dd.virtualfield(dd.ForeignKey('contacts.Partner'))
    def partner(self, row, ar):
        return row.partner

    @dd.virtualfield(dd.ForeignKey(dd.plugins.ledger.project_model))
    def project(self, row, ar):
        return row.project

    @dd.virtualfield(dd.ForeignKey('accounts.Account'))
    def account(self, row, ar):
        return row.account

    @dd.virtualfield(dd.ForeignKey(
        'sepa.Account', verbose_name=_("Bank account")))
    def bank_account(self, row, ar):
        return row.bank_account


class DebtsByAccount(ExpectedMovements):
    master = 'accounts.Account'

    @classmethod
    def get_data_rows(cls, ar, **flt):
        account = ar.master_instance
        if account is None:
            return []
        if not account.clearable:
            return []
        flt.update(cleared=False, account=account)
        # ignore trade_type to avoid overriding account
        ar.param_values.trade_type = None
        return super(DebtsByAccount, cls).get_data_rows(ar, **flt)

dd.inject_action('accounts.Account', due=dd.ShowSlaveTable(DebtsByAccount))


class DebtsByPartner(ExpectedMovements):
    master = 'contacts.Partner'
    #~ column_names = 'due_date debts payments balance'

    @classmethod
    def get_dc(cls, ar=None):
        return CREDIT

    @classmethod
    def get_data_rows(cls, ar, **flt):
        partner = ar.master_instance
        if partner is None:
            return []
        flt.update(cleared=False, partner=partner)
        return super(DebtsByPartner, cls).get_data_rows(ar, **flt)

dd.inject_action('contacts.Partner', due=dd.ShowSlaveTable(DebtsByPartner))


class PartnerVouchers(Vouchers):
    editable = True

    parameters = dict(
        project=dd.ForeignKey(
            dd.plugins.ledger.project_model, blank=True, null=True),
        state=VoucherStates.field(blank=True),
        partner=dd.ForeignKey('contacts.Partner', blank=True, null=True),
        cleared=dd.YesNo.field(_("Show cleared vouchers"), blank=True),
        **Vouchers.parameters)
    params_layout = "partner project state journal start_period end_period cleared"
    params_panel_hidden = True

    @classmethod
    def get_simple_parameters(cls):
        s = super(PartnerVouchers, cls).get_simple_parameters()
        s |= set(['partner', 'state'])
        return s

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(PartnerVouchers, cls).get_request_queryset(ar)
        # movement_set__partner=models.F('partner'))
        if ar.param_values.cleared == dd.YesNo.yes:
            qs = qs.exclude(movement__cleared=False)
        elif ar.param_values.cleared == dd.YesNo.no:
            qs = qs.filter(movement__cleared=False)
        return qs


def mvtsum(**fkw):
    d = rt.modules.ledger.Movement.objects.filter(
        **fkw).aggregate(models.Sum('amount'))
    return d['amount__sum'] or ZERO


class AccountsBalance(dd.VirtualTable):
    """A table which shows a list of general ledger accounts during the
    observed period, showing their old and new balances and the sum of
    debit and credit movements.

    """
    required_roles = dd.login_required(AccountingReader)
    auto_fit_column_widths = True
    column_names = "ref description old_d old_c during_d during_c new_d new_c"
    slave_grid_format = 'html'
    abstract = True

    parameters = mixins.Yearly(
        # include_vat = models.BooleanField(
        #     verbose_name=dd.apps.vat.verbose_name),
    )

    params_layout = "start_date end_date"
    
    @classmethod
    def rowmvtfilter(self, row):
        raise NotImplementedError()

    @classmethod
    def get_request_queryset(self, ar):
        raise NotImplementedError()

    @classmethod
    def get_data_rows(self, ar):
        pv = ar.param_values
        # mi = ar.master_instance
        # if mi is None:
        #     return
        qs = self.get_request_queryset(ar)
        for row in qs:
            flt = self.rowmvtfilter(row)
            row.old = Balance(
                mvtsum(
                    value_date__lt=pv.start_date,
                    dc=DEBIT, **flt),
                mvtsum(
                    value_date__lt=pv.start_date,
                    dc=CREDIT, **flt))
            row.during_d = mvtsum(
                value_date__gte=pv.start_date,
                value_date__lte=pv.end_date,
                dc=DEBIT, **flt)
            row.during_c = mvtsum(
                value_date__gte=pv.start_date,
                value_date__lte=pv.end_date,
                dc=CREDIT, **flt)
            if row.old.d or row.old.c or row.during_d or row.during_c:
                row.new = Balance(row.old.d + row.during_d,
                                  row.old.c + row.during_c)
                yield row

    @dd.displayfield(_("Reference"))
    def ref(self, row, ar):
        return row.ref

    @dd.displayfield(_("Description"))
    def description(self, row, ar):
        return row.obj2href(ar)

    @dd.virtualfield(dd.PriceField(_("Debit\nbefore")))
    def old_d(self, row, ar):
        return row.old.d

    @dd.virtualfield(dd.PriceField(_("Credit\nbefore")))
    def old_c(self, row, ar):
        return row.old.c

    @dd.virtualfield(dd.PriceField(_("Debit")))
    def during_d(self, row, ar):
        return row.during_d

    @dd.virtualfield(dd.PriceField(_("Credit")))
    def during_c(self, row, ar):
        return row.during_c

    @dd.virtualfield(dd.PriceField(_("Debit\nafter")))
    def new_d(self, row, ar):
        return row.new.c

    @dd.virtualfield(dd.PriceField(_("Credit\nafter")))
    def new_c(self, row, ar):
        return row.new.d
    

class GeneralAccountsBalance(AccountsBalance):

    label = _("General Accounts Balances")

    @classmethod
    def get_request_queryset(self, ar):
        return rt.modules.accounts.Account.objects.order_by(
            'group__ref', 'ref')

    @classmethod
    def rowmvtfilter(self, row):
        return dict(account=row)


class PartnerAccountsBalance(AccountsBalance):
    trade_type = NotImplementedError

    @classmethod
    def get_request_queryset(self, ar):
        return rt.modules.contacts.Partner.objects.order_by('name')

    @classmethod
    def rowmvtfilter(self, row):
        a = self.trade_type.get_partner_account()
        # TODO: what if a is None?
        return dict(partner=row, account=a)

    @dd.displayfield(_("Ref"))
    def ref(self, row, ar):
        return str(row.pk)


class CustomerAccountsBalance(PartnerAccountsBalance):
    label = _("Customer Accounts Balances")
    trade_type = TradeTypes.sales


class SupplierAccountsBalance(PartnerAccountsBalance):
    label = _("Supplier Accounts Balances")
    trade_type = TradeTypes.purchases


##


class DebtorsCreditors(dd.VirtualTable):
    required_roles = dd.login_required(AccountingReader)
    auto_fit_column_widths = True
    column_names = "age due_date partner partner_id balance vouchers"
    slave_grid_format = 'html'
    abstract = True

    parameters = mixins.Today()
    # params_layout = "today"

    d_or_c = NotImplementedError

    @classmethod
    def rowmvtfilter(self, row):
        raise NotImplementedError()

    @classmethod
    def get_data_rows(self, ar):
        rows = []
        mi = ar.master_instance
        if mi is None:  # called directly from main menu
            if ar.param_values is None:
                return rows
            end_date = ar.param_values.today
        else:   # called from Situation report
            end_date = mi.today
        
        qs = rt.modules.contacts.Partner.objects.order_by('name')
        for row in qs:
            row._balance = ZERO
            row._due_date = None
            row._expected = tuple(
                get_due_movements(
                    self.d_or_c,
                    partner=row,
                    value_date__lte=end_date))
            for dm in row._expected:
                row._balance += dm.balance
                if dm.due_date is not None:
                    if row._due_date is None or row._due_date > dm.due_date:
                        row._due_date = dm.due_date
                # logger.info("20140105 %s %s", row, dm)

            if row._balance > ZERO:
                rows.append(row)

        def k(a):
            return a._due_date
        rows.sort(key=k)
        return rows

    # @dd.displayfield(_("Partner"))
    # def partner(self, row, ar):
    #     return ar.obj2html(row)

    @dd.virtualfield(models.ForeignKey('contacts.Partner'))
    def partner(self, row, ar):
        return row

    @dd.virtualfield(models.IntegerField(_("ID")))
    def partner_id(self, row, ar):
        return row.pk

    @dd.virtualfield(dd.PriceField(_("Balance")))
    def balance(self, row, ar):
        return row._balance

    @dd.virtualfield(models.DateField(_("Due date")))
    def due_date(self, row, ar):
        return row._due_date

    @dd.virtualfield(models.IntegerField(_("Age")))
    def age(self, row, ar):
        dd = ar.param_values.today - row._due_date
        return dd.days

    @dd.displayfield(_("Vouchers"))
    def vouchers(self, row, ar):
        matches = [dm.match for dm in row._expected]
        return E.span(', '.join(matches))

    # @dd.displayfield(_("Actions"))
    # def actions(self, row, ar):
    #     # TODO
    #     return E.span("[Show debts] [Issue reminder]")


class Debtors(DebtorsCreditors):
    label = _("Debtors")
    help_text = _("List of partners who are in debt towards us "
                  "(usually customers).")
    d_or_c = CREDIT


class Creditors(DebtorsCreditors):
    label = _("Creditors")
    help_text = _("List of partners who are giving credit to us "
                  "(usually suppliers).")

    d_or_c = DEBIT

##


class Situation(Report):
    """
    A report consisting of the following tables:

   -  :class:`Debtors`
   -  :class:`Creditors`

    """
    label = _("Situation")
    help_text = _("Overview of the financial situation on a given date.")
    required_roles = dd.login_required(AccountingReader)

    parameters = mixins.Today()

    report_items = (Debtors, Creditors)


class ActivityReport(Report):
    """Overview of the financial activity during a given period.

    A report consisting of the following tables:

    - :class:`GeneralAccountsBalance`
    - :class:`CustomerAccountsBalance`
    - :class:`SupplierAccountsBalance`

    """
    label = _("Activity Report")
    required_roles = dd.login_required(AccountingReader)

    parameters = mixins.Yearly(
        # include_vat = models.BooleanField(
        #     verbose_name=dd.apps.vat.verbose_name),
    )

    params_layout = "start_date end_date"
    #~ params_panel_hidden = True

    report_items = (
        GeneralAccountsBalance,
        CustomerAccountsBalance,
        SupplierAccountsBalance)


# MODULE_LABEL = dd.plugins.accounts.verbose_name

# def site_setup(site):
#     c = site.modules.contacts
#     for T in (c.Partners, c.Companies, c.Persons):
#         if not hasattr(T.detail_layout, 'ledger'):
#             T.add_detail_tab(
#                 "ledger",
#                 """
#                 ledger.VouchersByPartner
#                 ledger.MovementsByPartner
#                 """,
#                 label=MODULE_LABEL)


class Movements(dd.Table):
    """
    The base table for all tables working on :class:`Movement`.
    Defines filtering parameters and general behaviour.

    Subclassed by e.g. :class:`AllMovements`,
    :class:`MovementsByVoucher`,
    :class:`MovementsByAccount` and :class:`MovementsByPartner`.

    See also :class:`lino_xl.lib.ledger.models.Movement`.
    """
    
    model = 'ledger.Movement'
    required_roles = dd.login_required(LedgerUser)
    column_names = 'value_date voucher_link description \
    debit credit match_link cleared *'
    sum_text_column = 2
    order_by = ['id']

    editable = False
    parameters = mixins.ObservedDateRange(
        year=FiscalYears.field(blank=True),
        journal_group=JournalGroups.field(blank=True),
        partner=dd.ForeignKey('contacts.Partner', blank=True, null=True),
        project=dd.ForeignKey(
            dd.plugins.ledger.project_model, blank=True, null=True),
        account=dd.ForeignKey('accounts.Account', blank=True, null=True),
        journal=JournalRef(blank=True),
        cleared=dd.YesNo.field(_("Show cleared movements"), blank=True))
    params_layout = """
    start_period end_period start_date end_date cleared
    journal_group journal year project partner account"""

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(Movements, cls).get_request_queryset(ar)

        pv = ar.param_values
        if pv.cleared == dd.YesNo.yes:
            qs = qs.filter(cleared=True)
        elif pv.cleared == dd.YesNo.no:
            qs = qs.filter(cleared=False)

        if pv.start_date:
            qs = qs.filter(value_date__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(value_date__lte=pv.end_date)
            
        # if ar.param_values.partner:
        #     qs = qs.filter(partner=ar.param_values.partner)
        # if ar.param_values.paccount:
        #     qs = qs.filter(account=ar.param_values.paccount)
        if pv.year:
            qs = qs.filter(voucher__accounting_period__year=pv.year)
        if pv.journal_group:
            qs = qs.filter(voucher__journal__journal_group=pv.journal_group)
        if pv.journal:
            qs = qs.filter(voucher__journal=pv.journal)
        return qs

    @classmethod
    def get_sum_text(self, ar, sums):
        bal = sums['debit'] - sums['credit']
        return _("Balance {1} ({0} movements)").format(
            ar.get_total_count(), bal)

    @classmethod
    def get_simple_parameters(cls):
        p = super(Movements, cls).get_simple_parameters()
        p.add('partner')
        p.add('project')
        # p.add('journal_group')
        # p.add('year')
        p.add('account')
        return p

    @classmethod
    def get_title_tags(cls, ar):
        for t in super(Movements, cls).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.journal is not None:
            yield pv.journal.ref
        if pv.journal_group is not None:
            yield unicode(pv.journal_group)
        if pv.year is not None:
            yield unicode(pv.year)
        if pv.cleared == dd.YesNo.no:
            yield unicode(_("only uncleared"))
        elif pv.cleared == dd.YesNo.yes:
            yield unicode(_("only cleared"))

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher.narration:
            elems.append(voucher.narration)
        p = voucher.get_partner()
        if p is not None:
            elems.append(ar.obj2html(p))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))


class AllMovements(Movements):
    """
    Displayed by :menuselection:`Explorer --> Accounting --> Movements`.

    See also :class:`lino_xl.lib.ledger.models.Movement`.
    """
    required_roles = dd.login_required(LedgerStaff)


class MovementsByVoucher(Movements):
    """Show the ledger movements of a voucher.

    See also :class:`lino_xl.lib.ledger.models.Movement`.
    """
    master_key = 'voucher'
    column_names = 'seqno project partner account debit credit match_link cleared *'
    sum_text_column = 3
    # auto_fit_column_widths = True
    slave_grid_format = "html"


class MovementsByPartner(Movements):
    """Show the ledger movements of a partner.
    See also :class:`lino_xl.lib.ledger.models.Movement`.
    """
    master_key = 'partner'
    order_by = ['-value_date']
    # slave_grid_format = "html"
    slave_grid_format = "summary"
    # auto_fit_column_widths = True

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByPartner, cls).param_defaults(ar, **kw)
        # kw.update(cleared=dd.YesNo.no)
        kw.update(year='')
        return kw

    @classmethod
    def setup_request(self, ar):
        ar.no_data_text = _("No uncleared movements")

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher.narration:
            elems.append(voucher.narration)
        p = voucher.get_partner()
        if p is not None and p != ar.master_instance:
            elems.append(ar.obj2html(p))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))

    @classmethod
    def get_slave_summary(cls, obj, ar):
        """The :meth:`summary view <lino.core.actors.Actor.get_slave_summary>`
        for this table.

        """
        elems = []
        sar = ar.spawn(rt.models.ledger.Movements, param_values=dict(
            cleared=dd.YesNo.no, partner=obj))
        bal = ZERO
        for mvt in sar:
            if mvt.dc:
                bal -= mvt.amount
            else:
                bal += mvt.amount
        txt = _("{0} open movements ({1} {2})").format(
            sar.get_total_count(), bal, dd.plugins.ledger.currency_symbol)

        elems.append(ar.href_to_request(sar, txt))
        return ar.html_text(E.div(*elems))
        # return E.div(class_="htmlText", *elems)


class MovementsByProject(MovementsByPartner):
    """Show the ledger movements of a project.
    See also :class:`lino_xl.lib.ledger.models.Movement`.
    """
    master_key = 'project'
    slave_grid_format = "html"

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByPartner, cls).param_defaults(ar, **kw)
        kw.update(cleared=dd.YesNo.no)
        kw.update(year='')
        return kw

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher.narration:
            elems.append(voucher.narration)
        p = voucher.get_partner()
        if p is not None:
            elems.append(ar.obj2html(p))
        if self.partner and self.partner != p:
            elems.append(ar.obj2html(self.partner))
        return E.p(*join_elems(elems, " / "))


class MovementsByAccount(Movements):
    """Shows the movements done on a given general account.

    See also :class:`lino_xl.lib.ledger.models.Movement`.
    
    .. attribute:: description

        A virtual field showing a comma-separated list of the
        following items:

        - voucher narration
        - voucher partner
        - transaction's partner
        - transaction's project

    """
    master_key = 'account'
    order_by = ['-value_date']
    # auto_fit_column_widths = True
    slave_grid_format = "html"

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByAccount, cls).param_defaults(ar, **kw)
        if ar.master_instance is not None and ar.master_instance.clearable:
            kw.update(cleared=dd.YesNo.no)
            kw.update(year='')
        return kw

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        voucher = self.voucher.get_mti_leaf()
        if voucher.narration:
            elems.append(voucher.narration)
        p = voucher.get_partner()
        if p is not None:
            elems.append(ar.obj2html(p))
        if self.partner:
            elems.append(ar.obj2html(self.partner))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))


class MovementsByMatch(Movements):
    """Show all movements having a given :attr:`match`.

    This is another example of a slave table whose master is not a
    database object, and the first example of a slave table whose
    master is a simple string.

    """
    column_names = 'value_date voucher_link description '\
                   'debit credit cleared *'
    master = six.text_type  # 'ledger.Matching'
    order_by = ['-value_date']
    variable_row_height = True

    details_of_master_template = _("%(details)s matching '%(master)s'")

    @classmethod
    def get_master_instance(self, ar, model, pk):
        """No database lookup, just return the primary key"""
        return pk

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(MovementsByMatch, cls).get_request_queryset(ar)
        qs = qs.filter(match=ar.master_instance)
        return qs

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        if self.voucher.narration:
            elems.append(self.voucher.narration)
        voucher = self.voucher.get_mti_leaf()
        p = voucher.get_partner()
        if p is not None and p != ar.master_instance:
            elems.append(ar.obj2html(p))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))


