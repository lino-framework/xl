# -*- coding: UTF-8 -*-
# Copyright 2008-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.db import models
from django.db.models import OuterRef, Subquery, Sum
from etgen.html import E

from lino import mixins
from lino.api import dd, rt, _
from lino.utils import join_elems
from lino.utils.report import Report
from .choicelists import TradeTypes, VoucherTypes, JournalGroups
from .choicelists import VoucherStates
from .mixins import JournalRef, PeriodRangeObservable
from .roles import AccountingReader, LedgerUser, LedgerStaff
from .utils import Balance
from .utils import DEBIT, CREDIT, ZERO


class Accounts(dd.Table):
    model = 'ledger.Account'
    required_roles = dd.login_required(LedgerStaff)
    order_by = ['ref']
    column_names = "description sheet_item needs_partner clearable ref *"
    insert_layout = """
    ref sheet_item
    name
    """
    detail_layout = """
    ref:10 common_account sheet_item id
    name
    needs_partner:30 clearable:30 default_amount:10
    ledger.MovementsByAccount
    """


class JournalDetail(dd.DetailLayout):
    main = """
    name ref:5
    journal_group:15 voucher_type:20 trade_type:20 seqno:5 id:5
    account partner build_method:20 template:20 uploads_volume
    dc force_sequence #invert_due_dc yearly_numbering auto_fill_suggestions auto_check_clearings must_declare preliminary
    printed_name
    MatchRulesByJournal
    """


class Journals(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'ledger.Journal'
    order_by = ["seqno"]
    column_names = "ref:5 name trade_type journal_group " \
                   "voucher_type force_sequence * seqno id"
    detail_layout = 'ledger.JournalDetail'
    insert_layout = dd.InsertLayout("""
    ref name
    journal_group
    voucher_type
    """, window_size=(60, 'auto'))


class JournalsOverview(Journals):
    required_roles = dd.login_required(LedgerUser)
    column_names = "description num_vouchers this_year this_month state_draft warnings *"
    display_mode = "summary"
    editable = False

    @classmethod
    def get_table_summary(cls, mi, ar):
        if ar is None:
            return None
        items = []
        for obj in cls.get_request_queryset(ar):
            elems = []
            table_class = obj.get_doc_report()
            sar = table_class.request(master_instance=obj)
            # elems.append(str(sar.get_total_count()))
            # elems.append(" ")
            # elems.append(ar.href_to_request(sar, text=str(obj)))
            elems.append(ar.href_to_request(
                sar, text="{} {}".format(sar.get_total_count(), obj)))
            if True:
                sar = table_class.insert_action.request_from(ar, master_instance=obj)
                # print(20170217, sar)
                sar.known_values.update(journal=obj)
                # txt = dd.babelattr(obj, 'printed_name')
                # btn = sar.ar2button(None, _("New {}").format(txt), icon_name=None)
                btn = sar.ar2button(label="⊕", icon_name=None) # U+2295 Circled Plus Unicode Character.
                # btn = sar.ar2button()
                # btn.set("style", "padding-left:10px")
                btn.set("style", "text-decoration:none")
                elems.append(" ")
                elems.append(btn)
            else:
                elems.append(" / ")
                elems.append(obj.insert_voucher_button(ar))
            items.append(E.li(*elems))
        return E.ul(*items)

    @dd.displayfield(_("Description"))
    def description(cls, obj, ar):
        elems = []
        elems.append(str(obj))
        # if ar.get_user().authenticated:
        elems.append(obj.insert_voucher_button(ar))
        return E.p(*join_elems(elems, " / "))

    @dd.requestfield(_("Total"))
    def num_vouchers(self, obj, ar):
        tbl = obj.get_doc_report()
        return tbl.request(master_instance=obj)

    @dd.requestfield(_("This year"))
    def this_year(self, obj, ar):
        tbl = obj.get_doc_report()
        AccountingPeriod = rt.models.ledger.AccountingPeriod
        # print(20190924, year)
        pv = dict()
        if issubclass(tbl.model, PeriodRangeObservable):
            pv.update(start_period=AccountingPeriod.get_default_for_date(dd.today().replace(month=1, day=1)))
            pv.update(end_period=AccountingPeriod.get_default_for_date(dd.today().replace(month=12, day=31)))
        return tbl.request(master_instance=obj, param_values=pv)

    @dd.requestfield(_("This month"))
    def this_month(self, obj, ar):
        tbl = obj.get_doc_report()
        AccountingPeriod = rt.models.ledger.AccountingPeriod
        # print(20190924, year)
        pv = dict()
        if issubclass(tbl.model, PeriodRangeObservable):
            pv.update(start_period=AccountingPeriod.get_default_for_date(dd.today()))
        return tbl.request(master_instance=obj, param_values=pv)

    @dd.requestfield(_("Unfinished"))
    def state_draft(self, obj, ar):
        tbl = obj.get_doc_report()
        pv = dict(state=VoucherStates.draft)
        return tbl.request(master_instance=obj, param_values=pv)

    @dd.displayfield(_("Warnings"))
    def warnings(cls, self, ar):
        elems = []
        # elems.append(gettext("Everything ok"))
        return E.p(*join_elems(elems, " / "))


class ByJournal(dd.Table):
    # order_by = ["-entry_date", '-id']
    order_by = ["-accounting_period__year", "-number"]
    master_key = 'journal'
    # start_at_bottom = True
    required_roles = dd.login_required(LedgerUser)
    params_layout = "start_period end_period state user"
    no_phantom_row = True

    @classmethod
    def get_title_base(self, ar):
        """Without this override we would have a title like "Invoices of
        journal <Invoices>".  But we want just "Invoices".

        """
        return str(ar.master_instance)

    @classmethod
    def create_journal(cls, trade_type=None, account=None, **kw):
        vt = VoucherTypes.get_for_table(cls)
        if isinstance(trade_type, str):
            trade_type = TradeTypes.get_by_name(trade_type)
        if isinstance(account, str):
            account = rt.models.ledger.Account.get_by_ref(account)
        if account is not None:
            kw.update(account=account)
        return rt.models.ledger.Journal(
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
    column_names = "ref name months days end_of_month worker *"
    detail_layout = """
    ref months days end_of_month worker
    name
    printed_text
    """


class Vouchers(dd.Table):
    abstract = True
    required_roles = dd.login_required(LedgerUser)
    model = 'ledger.Voucher'
    editable = False
    order_by = ["entry_date", "number"]
    column_names = "entry_date number *"
    parameters = dict(
        year=dd.ForeignKey('ledger.FiscalYear', blank=True),
        journal=JournalRef(blank=True))
    params_layout = "journal start_period end_period #state user"

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        qs = super(Vouchers, cls).get_request_queryset(ar, **kwargs)
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


class MatchRulesByJournal(MatchRules):
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
        account=dd.ForeignKey('ledger.Account', blank=True),
        partner=dd.ForeignKey('contacts.Partner', blank=True),
        project=dd.ForeignKey(dd.plugins.ledger.project_model, blank=True),
        show_sepa=dd.YesNo.field(_("With SEPA"), blank=True),
        same_dc=dd.YesNo.field(_("Same D/C"), blank=True),
    )
    params_layout = """
    trade_type date_until from_journal for_journal
    project partner account show_sepa same_dc"""

    @classmethod
    def get_dc(cls, ar=None):
        return CREDIT

    @classmethod
    def get_data_rows(cls, ar, **flt):
        #~ if ar.param_values.journal:
            #~ pass
        pv = ar.param_values
        # if pv is None:
        #     raise Exception("No pv in %s" % ar)
        if pv.trade_type:
            flt.update(account=pv.trade_type.get_main_account())
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

        if pv.same_dc == dd.YesNo.yes:
            flt.update(dc=cls.get_dc(ar))
        elif pv.same_dc == dd.YesNo.no:
            flt.update(dc=not cls.get_dc(ar))

        if pv.date_until is not None:
            flt.update(value_date__lte=pv.date_until)
        if pv.for_journal is not None:
            accounts = rt.models.ledger.Account.objects.filter(
                matchrule__journal=pv.for_journal).distinct()
            flt.update(account__in=accounts)
        if pv.from_journal is not None:
            flt.update(voucher__journal=pv.from_journal)
        flt = models.Q(**flt)
        if ar.quick_search:
            flt &= rt.models.contacts.Partner.quick_search_filter(
                ar.quick_search, prefix='partner__')

        return rt.models.ledger.get_due_movements(cls.get_dc(ar), flt)

    @classmethod
    def get_pk_field(self):
        return rt.models.ledger.Movement._meta.pk

    @classmethod
    def get_row_by_pk(cls, ar, pk):
        # this is tricky.
        # for i in ar.data_iterator:
        #     if i.id == pk:
        #         return i
        # raise Exception("Not found: %s in %s" % (pk, ar))
        mvt = rt.models.ledger.Movement.objects.get(pk=pk)
        dm = rt.models.ledger.DueMovement(cls.get_dc(ar), mvt)
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

    @dd.virtualfield(dd.ForeignKey('ledger.Account'))
    def account(self, row, ar):
        return row.account

    @dd.virtualfield(dd.ForeignKey(
        'sepa.Account', verbose_name=_("Bank account")))
    def bank_account(self, row, ar):
        return row.bank_account


class DebtsByAccount(ExpectedMovements):
    master = 'ledger.Account'

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

dd.inject_action('ledger.Account', due=dd.ShowSlaveTable(DebtsByAccount))


class DebtsByPartner(ExpectedMovements):
    master = 'contacts.Partner'
    #~ column_names = 'due_date debts payments balance'

    @classmethod
    def get_dc(cls, ar=None):
        return DEBIT

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
        for s in super(PartnerVouchers, cls).get_simple_parameters():
            yield s
        yield 'partner'

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        qs = super(PartnerVouchers, cls).get_request_queryset(ar, **kwargs)
        # movement_set__partner=models.F('partner'))
        pv = ar.param_values
        if pv.cleared == dd.YesNo.yes:
            qs = qs.exclude(movement__cleared=False)
        elif pv.cleared == dd.YesNo.no:
            qs = qs.filter(movement__cleared=False)
        return qs



def mvtsum(**fkw):
    d = rt.models.ledger.Movement.objects.filter(
        **fkw).aggregate(models.Sum('amount'))
    return d['amount__sum'] or ZERO

class AccountingPeriodRange(dd.ParameterPanel):
    def __init__(self,
                 verbose_name_start=_("Period from"),
                 verbose_name_end=_("until"), **kwargs):
        kwargs.update(
            start_period=dd.ForeignKey(
                'ledger.AccountingPeriod',
                blank=True, null=True,
                help_text=_("Start of observed period range"),
                verbose_name=verbose_name_start),
            end_period=dd.ForeignKey(
                'ledger.AccountingPeriod',
                blank=True, null=True,
                help_text=_(
                    "Optional end of observed period range. "
                    "Leave empty to consider only the Start period."),
                verbose_name=verbose_name_end))
        super(AccountingPeriodRange, self).__init__(**kwargs)

    def check_values(self, pv):
        if not pv.start_period:
            raise Warning(_("Select at least a start period"))
        if pv.end_period:
            if str(pv.start_period) > str(pv.end_period):
                raise Warning(_("End period must be after start period"))

    def get_title_tags(self, ar):
        pv = ar.param_values
        if pv.start_period:
            if pv.end_period:
                yield _("Periods {}...{}").format(
                    pv.start_period, pv.end_period)
            else:
                yield _("Period {}").format(pv.start_period)
        else:
            yield str(_("All periods"))

class AccountBalances(dd.Table):
    editable = False
    required_roles = dd.login_required(AccountingReader)
    auto_fit_column_widths = True
    column_names = "description old_d old_c empty_column:1 during_d during_c empty_column:1 new_d new_c"
    display_mode = 'html'
    abstract = True
    params_panel_hidden = False
    use_as_default_table = False

    parameters = AccountingPeriodRange()
    params_layout = "start_period end_period"

    @classmethod
    def rowmvtfilter(self):
        raise NotImplementedError()

    @classmethod
    def get_request_queryset(self, ar, **kwargs):

        # see https://docs.djangoproject.com/en/1.11/ref/models/expressions/#using-aggregates-within-a-subquery-expression
        AccountingPeriod = rt.models.ledger.AccountingPeriod
        pv = ar.param_values
        sp = pv.start_period or AccountingPeriod.get_default_for_date(
            dd.today())
        ep = pv.end_period or sp

        qs = super(AccountBalances, self).get_request_queryset(ar)

        flt = self.rowmvtfilter(ar)
        oldflt = dict()
        oldflt.update(flt)
        duringflt = dict()
        duringflt.update(flt)
        during_periods = AccountingPeriod.objects.filter(
            ref__gte=sp.ref, ref__lte=ep.ref)
        before_periods = AccountingPeriod.objects.filter(
            ref__lt=sp.ref)
        oldflt.update(voucher__accounting_period__in=before_periods)
        duringflt.update(voucher__accounting_period__in=during_periods)

        outer_link = self.model._meta.model_name

        def addann(kw, name, dc, flt):
            mvts = rt.models.ledger.Movement.objects.filter(dc=dc, **flt)
            mvts = mvts.order_by()
            mvts = mvts.values(outer_link)  # this was the important thing
            mvts = mvts.annotate(total=Sum(
                'amount', output_field=dd.PriceField()))
            mvts = mvts.values('total')
            kw[name] = Subquery(mvts, output_field=dd.PriceField())

        kw = dict()
        addann(kw, 'old_d', DEBIT, oldflt)
        addann(kw, 'old_c', CREDIT, oldflt)
        addann(kw, 'during_d', DEBIT, duringflt)
        addann(kw, 'during_c', CREDIT, duringflt)

        qs = qs.annotate(**kw)

        qs = qs.exclude(
            old_d=ZERO, old_c=ZERO,
            during_d=ZERO, during_c=ZERO)

        # print("20170930 {}".format(qs.query))
        return qs

    @classmethod
    def new_balance(cls, row):
        return Balance(row.old_d, row.old_c) + Balance(
            row.during_d, row.during_c)

    @classmethod
    def normal_dc(cls, row, ar):
        # raise NotImplementedError()
        return DEBIT  # row.normal_dc

    @dd.displayfield(_("Reference"))
    def ref(self, row, ar):
        return row.ref

    @dd.displayfield(_("Description"))
    def description(self, row, ar):
        # print(20180831, ar.renderer, ar.user)
        return row.obj2href(ar)

    @dd.virtualfield(dd.PriceField(_("Old balance")))
    def old_dc(self, row, ar):
        return Balance(row.old_d, row.old_c).value(
            self.normal_dc(row, ar))

    @dd.virtualfield(dd.PriceField(_("Movements")))
    def during_dc(self, row, ar):
        return Balance(row.during_d, row.during_c).value(
            self.normal_dc(row, ar))

    @dd.virtualfield(dd.PriceField(_("New balance")))
    def new_dc(self, row, ar):
        return self.new_balance(row).value(self.normal_dc(row, ar))

    @dd.virtualfield(dd.PriceField(_("Debit before")))
    def old_d(self, row, ar):
        return Balance(row.old_d, row.old_c).d

    @dd.virtualfield(dd.PriceField(_("Credit before")))
    def old_c(self, row, ar):
        return Balance(row.old_d, row.old_c).c

    @dd.virtualfield(dd.PriceField(_("Debit")))
    def during_d(self, row, ar):
        return row.during_d

    @dd.virtualfield(dd.PriceField(_("Credit")))
    def during_c(self, row, ar):
        return row.during_c

    @dd.virtualfield(dd.PriceField(_("Debit after")))
    def new_d(self, row, ar):
        return self.new_balance(row).d

    @dd.virtualfield(dd.PriceField(_("Credit after")))
    def new_c(self, row, ar):
        return self.new_balance(row).c

    @dd.displayfield("", max_length=0)
    def empty_column(self, row, ar):
        return ''



class GeneralAccountBalances(AccountBalances, Accounts):

    label = _("General Account Balances")
    # model = 'ledger.Account'
    # order_by = ['group__ref', 'ref']
    order_by = ['ref']

    @classmethod
    def rowmvtfilter(self, ar):
        return dict(account=OuterRef('pk'))

contacts = dd.resolve_app('contacts')
# from lino_xl.lib.contacts.desktop import Partners
# print "20180831", dir(contacts)

class PartnerBalancesByTradeType(AccountBalances, contacts.Partners):

    order_by = ['name', 'id']
    column_names = "description old_dc during_d during_c new_dc"

    @classmethod
    def get_title_base(self, ar):
        return _("Partner Account Balances {}").format(ar.master_instance)

    @classmethod
    def rowmvtfilter(self, ar):
        tt = ar.master_instance
        if tt is None:
            return
        a = tt.get_main_account()
        return dict(partner=OuterRef('pk'), account=a)

    @dd.displayfield(_("Ref"))
    def ref(self, row, ar):
        return str(row.pk)

    @classmethod
    def normal_dc(cls, row, ar):
        tt = ar.master_instance
        if tt is None:
            return DEBIT
        return tt.dc


# class CustomerAccountsBalance(PartnerAccountsBalance):
#     label = _("Customer Accounts Balance")
#     trade_type = TradeTypes.sales


# class SupplierAccountsBalance(PartnerAccountsBalance):
#     label = _("Supplier Accounts Balance")
#     trade_type = TradeTypes.purchases


##


class DebtorsCreditors(dd.VirtualTable):
    required_roles = dd.login_required(AccountingReader)
    auto_fit_column_widths = True
    column_names = "age due_date partner partner_id balance vouchers"
    display_mode = 'html'
    abstract = True

    parameters = mixins.Today()
    # params_layout = "today"

    d_or_c = NotImplementedError

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
        get_due_movements = rt.models.ledger.get_due_movements
        qs = rt.models.contacts.Partner.objects.order_by('name')
        for row in qs:
            row._balance = ZERO
            row._due_date = None
            row._expected = tuple(
                get_due_movements(
                    self.d_or_c,
                    models.Q(partner=row, value_date__lte=end_date)))
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

    @dd.virtualfield(dd.ForeignKey('contacts.Partner'))
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
    d_or_c = DEBIT


class Creditors(DebtorsCreditors):
    label = _("Creditors")
    help_text = _("List of partners who are giving credit to us "
                  "(usually suppliers).")

    d_or_c = CREDIT

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


# class ActivityReport(Report):
#     """Overview of the financial activity during a given period.

#     A report consisting of the following tables:

#     - :class:`GeneralAccountsBalance`
#     - :class:`CustomerAccountsBalance`
#     - :class:`SupplierAccountsBalance`

#     """
#     label = _("Activity Report")
#     required_roles = dd.login_required(AccountingReader)

#     parameters = mixins.Yearly(
#         # include_vat = models.BooleanField(
#         #     verbose_name=dd.plugins.vat.verbose_name),
#     )

#     params_layout = "start_date end_date"
#     #~ params_panel_hidden = True

#     report_items = (
#         GeneralAccountsBalance,
#         CustomerAccountsBalance,
#         SupplierAccountsBalance)

# class AccountingReport(Report):
#     label = _("Accounting Report")
#     auto_apply_params = False
#     required_roles = dd.login_required(AccountingReader)
#     params_panel_hidden = False
#     parameters = AccountingPeriodRange(
#         with_general = models.BooleanField(
#             verbose_name=_("General accounts"), default=True),
#         with_balances = models.BooleanField(
#             verbose_name=_("Balance lists"), default=True),
#         with_activity = models.BooleanField(
#             verbose_name=_("Activity lists"), default=True))
#     build_method = 'appypdf'

#     @classmethod
#     def setup_parameters(cls, fields):
#         params_layout = """
#         start_period end_period with_balances with_activity with_general"""

#         if dd.is_installed('ana'):
#             k = 'with_analytic'
#             fields[k] = models.BooleanField(
#                 verbose_name=_("Analytic accounts"), default=True)
#             params_layout += ' ' + k

#         params_layout += '\n'
#         for tt in TradeTypes.get_list_items():
#             k = 'with_'+tt.name
#             fields[k] = models.BooleanField(
#                 verbose_name=tt.text, default=True)
#             params_layout += ' ' + k
#         # params_layout += ' go_button'
#         cls.params_layout = params_layout
#         super(AccountingReport, cls).setup_parameters(fields)

#     @classmethod
#     def get_story(cls, self, ar):
#         pv = ar.param_values
#         cls.check_params(pv)
#         # if not pv.start_period:
#         #     yield E.p(gettext("Select at least a start period"))
#         #     return
#         bpv = dict(start_period=pv.start_period, end_period=pv.end_period)
#         balances = []
#         if pv.with_general:
#             balances.append(ar.spawn(
#                 GeneralAccountBalances, param_values=bpv))
#         if dd.is_installed('ana'):
#             if pv.with_analytic:
#                 balances.append(ar.spawn(
#                     rt.models.ana.AnalyticAccountBalances,
#                     param_values=bpv))
#         for tt in TradeTypes.get_list_items():
#             k = 'with_'+tt.name
#             if pv[k]:
#                 balances.append(ar.spawn(
#                     PartnerBalancesByTradeType,
#                     master_instance=tt, param_values=bpv))
#         # if pv.with_sales:
#         #     balances.append(CustomerAccountsBalance)
#         # if pv.with_purchases:
#         #     balances.append(SupplierAccountsBalance)
#         if pv.with_balances:
#             for sar in balances:
#                 yield E.h1(str(sar.get_title()))
#                 yield sar
#                 # yield E.h1(B.label)
#                 # yield B.request(param_values=bpv)


class Movements(dd.Table):
    model = 'ledger.Movement'
    required_roles = dd.login_required(LedgerUser)
    column_names = 'value_date voucher_link description \
    debit credit match_link cleared *'
    sum_text_column = 2
    order_by = ['id']

    editable = False
    parameters = mixins.ObservedDateRange(
        year=dd.ForeignKey('ledger.FiscalYear', blank=True),
        journal_group=JournalGroups.field(blank=True),
        partner=dd.ForeignKey('contacts.Partner', blank=True, null=True),
        project=dd.ForeignKey(
            dd.plugins.ledger.project_model, blank=True, null=True),
        account=dd.ForeignKey('ledger.Account', blank=True, null=True),
        journal=JournalRef(blank=True),
        cleared=dd.YesNo.field(_("Show cleared movements"), blank=True))
    params_layout = """
    start_period end_period start_date end_date cleared
    journal_group journal year project partner account"""

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        qs = super(Movements, cls).get_request_queryset(ar, **kwargs)

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
        p = list(super(Movements, cls).get_simple_parameters())
        p.append('partner')
        p.append('project')
        # p.append('journal_group')
        # p.append('year')
        p.append('account')
        return p

    @classmethod
    def get_title_tags(cls, ar):
        for t in super(Movements, cls).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.journal is not None:
            yield pv.journal.ref
        if pv.journal_group is not None:
            yield str(pv.journal_group)
        if pv.year is not None:
            yield str(pv.year)
        if pv.cleared == dd.YesNo.no:
            yield str(_("only uncleared"))
        elif pv.cleared == dd.YesNo.yes:
            yield str(_("only cleared"))

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        # raise Exception("20191003")
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher is not None:
            elems.extend(voucher.get_movement_description(self, ar))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))


class AllMovements(Movements):
    required_roles = dd.login_required(LedgerStaff)


class MovementsByVoucher(Movements):
    # master = 'ledger.Voucher'
    master_key = 'voucher'
    column_names = 'account project partner debit credit match_link cleared *'
    sum_text_column = 3
    # auto_fit_column_widths = True
    display_mode = "html"
    order_by = dd.plugins.ledger.remove_dummy(
        'value_date', 'account__ref', 'partner', 'project', 'id')


class MovementsByPartner(Movements):
    master_key = 'partner'
    # display_mode = "html"
    display_mode = "summary"
    # auto_fit_column_widths = True
    # order_by = ['-value_date', 'voucher__id', 'account__ref']
    order_by = dd.plugins.ledger.remove_dummy(
        '-value_date', 'voucher__id', 'account__ref', 'project', 'id')

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByPartner, cls).param_defaults(ar, **kw)
        # kw.update(cleared=dd.YesNo.no)
        kw.update(year=None)
        return kw

    @classmethod
    def setup_request(self, ar):
        ar.no_data_text = _("No uncleared movements")

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        # raise Exception("20191003")
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher is not None:
            elems.extend(voucher.get_movement_description(self, ar))
            # if voucher.narration:
            #     elems.append(voucher.narration)
            # p = voucher.get_partner()
            # if p is not None and p != ar.master_instance:
            #     elems.append(ar.obj2html(p))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " | "))

    @classmethod
    def get_table_summary(cls, mi, ar):
        elems = []
        sar = ar.spawn(rt.models.ledger.Movements, param_values=dict(
            cleared=dd.YesNo.no, partner=mi))
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


class MovementsByProject(MovementsByPartner):
    master_key = 'project'
    display_mode = "html"
    order_by = ['-value_date', 'partner', 'id']

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByPartner, cls).param_defaults(ar, **kw)
        kw.update(cleared=dd.YesNo.no)
        kw.update(year=None)
        return kw

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        # raise Exception("20191003")
        if ar is None:
            return ''
        elems = []
        elems.append(ar.obj2html(self.account))
        voucher = self.voucher.get_mti_leaf()
        if voucher is not None:
            elems.extend(voucher.get_movement_description(self, ar))
            # if voucher.narration:
            #     elems.append(voucher.narration)
            # p = voucher.get_partner()
            # if p is not None:
            #     elems.append(ar.obj2html(p))
            # if self.partner and self.partner != p:
            #     elems.append(ar.obj2html(self.partner))
        return E.p(*join_elems(elems, " / "))


class MovementsByAccount(Movements):
    master_key = 'account'
    column_names = 'value_date voucher_link description \
    debit credit match_link *'
    # order_by = ['-value_date']
    # auto_fit_column_widths = True
    display_mode = "html"
    # order_by = ['-value_date', 'account__ref', 'project', 'id']
    order_by = dd.plugins.ledger.remove_dummy(
        '-value_date', 'partner__name', 'project', 'id')

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MovementsByAccount, cls).param_defaults(ar, **kw)
        if ar.master_instance is not None and ar.master_instance.clearable:
            kw.update(cleared=dd.YesNo.no)
            kw.update(year=None)
        return kw

    @dd.displayfield(_("Description"))
    def description(cls, self, ar):
        if ar is None:
            return ''
        elems = []
        voucher = self.voucher.get_mti_leaf()
        if voucher is not None:
            elems.extend(voucher.get_movement_description(self, ar))
        #     if voucher.narration:
        #         elems.append(voucher.narration)
        #     p = voucher.get_partner()
        #     if p is not None:
        #         elems.append(ar.obj2html(p))
        # if self.partner:
        #     elems.append(ar.obj2html(self.partner))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))


class MovementsByMatch(Movements):
    column_names = 'value_date voucher_link description '\
                   'debit credit cleared *'
    master = str  # 'ledger.Matching'
    variable_row_height = True
    order_by = dd.plugins.ledger.remove_dummy(
        '-value_date', 'account__ref', 'project', 'id')

    details_of_master_template = _("%(details)s matching '%(master)s'")

    @classmethod
    def get_master_instance(self, ar, model, pk):
        """No database lookup, just return the primary key"""
        return pk

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        qs = super(MovementsByMatch, cls).get_request_queryset(ar, **kwargs)
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
        if voucher is not None:
            elems.extend(voucher.get_movement_description(self, ar))
            # p = voucher.get_partner()
            # if p is not None and p != ar.master_instance:
            #     elems.append(ar.obj2html(p))
            # elif self.partner:
            #     elems.append(ar.obj2html(self.partner))
        if self.project:
            elems.append(ar.obj2html(self.project))
        return E.p(*join_elems(elems, " / "))
