# -*- coding: UTF-8 -*-
# Copyright 2018-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# import datetime

from collections import OrderedDict
from django.db import models
from django.db.models import OuterRef, Subquery, Sum

from etgen.html import E

from lino.api import dd, rt, _
from lino.mixins import StructuredReferrable, Story
from lino_xl.lib.excerpts.mixins import Certifiable
from lino.utils.mldbc.mixins import BabelDesignated
# from lino_xl.lib.ledger.models import DebitOrCreditField
from lino_xl.lib.ledger.utils import DC, ZERO, Balance,myround
from lino_xl.lib.ledger.choicelists import DC, TradeTypes
#from lino_xl.lib.ledger.models import Voucher
#from lino_xl.lib.ledger.mixins import SequencedVoucherItem
from lino_xl.lib.ledger.mixins import PeriodRange
#from lino.modlib.system.choicelists import PeriodEvents
#from lino.modlib.summaries.mixins import SimpleSummary
#from lino_xl.lib.ledger.ui import ByJournal
from lino.modlib.users.mixins import UserPlan
from lino_xl.lib.ledger.roles import LedgerStaff

from .choicelists import SheetTypes, CommonItems, ref_max_length

# ENTRY_VALUES = "old_d old_c during_d during_c".split()

class Item(StructuredReferrable, BabelDesignated):
    class Meta:
        app_label = 'sheets'
        verbose_name = _("Sheet item")
        verbose_name_plural = _("Sheet items")
        abstract = dd.is_abstract_model(__name__, 'Item')


    dc = DC.field(_("Booking direction"))
    sheet_type = SheetTypes.field()
    common_item = CommonItems.field(blank=True)
    mirror_ref = models.CharField(
        _("Mirror"), max_length=ref_max_length, blank=True, null=True)


class Collector(object):
    def __init__(self, entry_model, fkname, outer_link, **rowmvtfilter):
        # entry_model is AccountEntry, PartnerEntry, ItemEntry or AnaAccountEntry
        # fkname is "account" or "partner" or "item" or "ana_account"
        self.entry_model = entry_model
        self.rowmvtfilter = rowmvtfilter
        self.rowmvtfilter[outer_link] = OuterRef('pk')
        self.fkname = fkname
        self.fk = entry_model._meta.get_field(fkname)
        self.outer_model = self.fk.remote_field.model
        self.outer_link = outer_link
        # self.outer_link = self.outer_model._meta.model_name
        # print(20180905, self.outer_link)

    def get_mvt_filter(self, **flt):
        flt.update(self.rowmvtfilter)
        return flt

    def addann(self, kw, name, dc, flt):
        mvts = rt.models.ledger.Movement.objects.filter(**flt)
        if dc == DC.debit:
            mvts = mvts.filter(amount__lt=0)
        else:
            # assert dc == DC.debit.opposite()
            mvts = mvts.filter(amount__gt=0)
        mvts = mvts.order_by()
        mvts = mvts.values(self.outer_link)  # this was the important thing
        mvts = mvts.annotate(total=Sum(
            'amount', output_field=dd.PriceField(decimal_places=14)))
            # For Django2 we need to set decimal_places to 14, which is the max
            # of decimal_places used in ReportEntry fields.
        mvts = mvts.values('total')
        kw[name] = Subquery(mvts, output_field=dd.PriceField(decimal_places=14))

    def create_entry(self, report, obj, **kwargs):
        kwargs.update(report=report)
        kwargs[self.fkname] = obj
        old = Balance(-(obj.old_d or ZERO), obj.old_c)
        kwargs.update(old_d=myround(old.d))
        kwargs.update(old_c=myround(old.c))
        kwargs.update(during_d=-myround(obj.during_d or ZERO))
        kwargs.update(during_c=myround(obj.during_c or ZERO))
        # if report.id == 1 and self.fkname == 'item':
        #     print("20201013 create_entry()", obj, kwargs)
        return self.entry_model(**kwargs)


class TradeTypeCollector(Collector):
    def __init__(self, tt, *args, **kwargs):
        self.trade_type = tt
        super(TradeTypeCollector, self).__init__(*args, **kwargs)

    def create_entry(self, *args, **kwargs):
        kwargs.update(trade_type=self.trade_type)
        return super(TradeTypeCollector, self).create_entry(*args, **kwargs)


class ReportEntry(dd.Model):
    class Meta:
        abstract = True

    show_in_site_search = False
    allow_cascaded_delete = ['report']

    report = dd.ForeignKey('sheets.Report')
    old_d = dd.PriceField(_("Debit before"), 14, default=ZERO)
    old_c = dd.PriceField(_("Credit before"), 14, default=ZERO)
    during_c = dd.PriceField(_("Credit"), 14, default=ZERO)
    during_d = dd.PriceField(_("Debit"), 14, default=ZERO)
    # old_d = dd.PriceField(_("Debit before"), 14, null=True, blank=True)
    # old_c = dd.PriceField(_("Credit before"), 14, null=True, blank=True)
    # during_d = dd.PriceField(_("Debit"), 14, null=True, blank=True)
    # during_c = dd.PriceField(_("Credit"), 14, null=True, blank=True)

    def new_balance(self):
        return Balance(self.old_d, self.old_c) + Balance(
            self.during_d, self.during_c)

    def value2html(self, ar):
        txt = dd.format_currency(self.value, False, True)
        if self.item.is_heading():
            # return E.b(txt)
            return E.div(E.b(txt), align="right")
        # return txt
        return E.div(txt, align="right")

    @dd.virtualfield(dd.PriceField(_("Debit after")))
    def new_d(self, ar):
        return self.new_balance().d

    @dd.virtualfield(dd.PriceField(_("Credit after")))
    def new_c(self, ar):
        return self.new_balance().c

    @dd.displayfield(_("Balance before"))
    def old_dc(self, ar):
        return str(Balance(self.old_d, self.old_c))

    # @dd.virtualfield(dd.PriceField(_("Balance after")))
    @dd.displayfield(_("Balance after"))
    def new_dc(self, ar):
        return str(self.new_balance())

    @classmethod
    def compute_sum_entries(cls, report):
        pass

    # def __str__(self):
    #     return str(self.description)

# ReportEntry.set_widget_options('old_dc', hide_sum=True)
# ReportEntry.set_widget_options('new_dc', hide_sum=True)


class AccountEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'AccountEntry')
        verbose_name = _("General account balance")
        verbose_name_plural = _("General account balances")

    account = dd.ForeignKey('ledger.Account')

    @dd.displayfield(_("Account"))
    def description(self, ar=None):
        # print(20180831, ar.renderer, ar.user)
        return self.account.description

    @classmethod
    def get_collectors(cls):
        yield Collector(cls, 'account', 'account')


class PartnerEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'PartnerEntry')
        verbose_name = _("Partner balance")
        verbose_name_plural = _("Partner balances")

    # allow_cascaded_delete = ['partner', 'report']

    partner = dd.ForeignKey('contacts.Partner')
    trade_type = TradeTypes.field()

    @dd.displayfield(_("Partner"))
    def description(self, ar=None):
        if ar is None:
            return str(self.partner)
        return self.partner.obj2href(ar)

    @classmethod
    def get_collectors(cls):
        # raise Exception("20191206 {}".format(list(TradeTypes.get_list_items())))
        for tt in TradeTypes.get_list_items():
            a = tt.get_main_account()
            if isinstance(a, rt.models.ledger.Account):  # might be MissingAccount
                yield TradeTypeCollector(
                    tt, cls, 'partner', 'partner', account=a)
            #else:
            #    raise Exception("20191206 {} is not an account".format(a))

    @classmethod
    def setup_parameters(cls, fields):
        fields.setdefault(
            'trade_type', TradeTypes.field(blank=True))
        super(PartnerEntry, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(self, ar, **filter):
        qs = super(PartnerEntry, self).get_request_queryset(ar, **filter)
        pv = ar.param_values
        tt = pv.trade_type
        if tt:
            qs = qs.filter(trade_type=tt)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(PartnerEntry, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.trade_type:
            yield str(pv.trade_type)

class ItemEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'ItemEntry')
        verbose_name = _("Sheet item entry")
        verbose_name_plural = _("Sheet item entries")

    # allow_cascaded_delete = ['item']

    item = dd.ForeignKey('sheets.Item')

    # def __init__(self, *args, **kwargs):
    #     super(ItemEntry, self).__init__(*args, **kwargs)

    def full_clean(self):
        si = self.item
        if si.mirror_ref and self.new_balance().value(si.dc) < 0:
            # print("20201013c", self.item, si.mirror_ref, self.new_balance())
            self.item = rt.models.sheets.Item.get_by_ref(si.mirror_ref)
        super(ItemEntry, self).full_clean()

    @dd.displayfield(_("Description"))
    def description(self, ar=None):
        # print(20180831, ar.renderer, ar.user)
        return self.item.description

    @classmethod
    def get_collectors(cls):
        yield Collector(cls, 'item', 'account__sheet_item')

    @classmethod
    def compute_sum_entries(cls, report):
        sum_items = []
        for i in rt.models.sheets.Item.objects.all():
            if len(i.ref) != ref_max_length:
                sum_items.append(cls(report=report, item=i))
        for entry in cls.objects.filter(report=report):
            for si in sum_items:
                if entry.item.ref.startswith(si.item.ref):
                    # print("20201013a sum_items", entry.item.ref, si.item.ref, entry.during_d)
                    si.old_d += entry.old_d
                    si.old_c += entry.old_c
                    si.during_d += entry.during_d
                    si.during_c += entry.during_c
        # print("20201013 sum_items", [(si.item.ref, si.old_d, si.old_c, si.during_d, si.during_c) for si in sum_items])
        for si in sum_items:
            if si.old_d or si.old_c or si.during_d or si.during_c:
                si.full_clean()
                si.save()


    # @classmethod
    # def setup_parameters(cls, fields):
    #     fields.setdefault(
    #         'sheet_type', SheetTypes.field())
    #     super(ItemEntry, cls).setup_parameters(fields)

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     qs = super(ItemEntry, self).get_request_queryset(ar, **filter)
    #     pv = ar.param_values
    #     if pv.sheet_type:
    #         qs = qs.filter(item__sheet_type=pv.sheet_type)
    #     return qs

    # @classmethod
    # def get_title_tags(self, ar):
    #     for t in super(ItemEntry, self).get_title_tags(ar):
    #         yield t
    #     pv = ar.param_values
    #     if pv.sheet_type:
    #         yield str(pv.sheet_type)

    @dd.virtualfield(dd.PriceField(_("Activa")))
    def activa(self, ar):
        if self.item.dc == DC.credit:
            return self.new_balance().value(DC.credit)

    @dd.virtualfield(dd.PriceField(_("Passiva")))
    def passiva(self, ar):
        if self.item.dc == DC.debit:
            return self.new_balance().value(DC.debit)

    @dd.virtualfield(dd.PriceField(_("Expenses")))
    def expenses(self, ar):
        if self.item.dc == DC.debit:
            return self.new_balance().value(DC.debit)

    @dd.virtualfield(dd.PriceField(_("Revenues")))
    def revenues(self, ar):
        if self.item.dc == DC.credit:
            return self.new_balance().value(DC.credit)


class AnaAccountEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'AnaAccountEntry')
        verbose_name = _("Analytic accounts balance")
        verbose_name_plural = _("Analytic accounts balances")

    ana_account = dd.ForeignKey('ana.Account')

    @dd.displayfield(_("Account"))
    def description(self, ar=None):
        return self.ana_account.description

    @classmethod
    def get_collectors(cls):
        yield Collector(cls, 'ana_account', 'ana_account')



class Report(UserPlan, PeriodRange, Certifiable, Story):

    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'Report')
        verbose_name = _("Accounting Report")
        verbose_name_plural = _("Accounting Reports")

    # account_entries = dd.ShowSlaveTable('sheets.AccountEntriesByReport')
    # partner_entries = dd.ShowSlaveTable('sheets.PartnerEntriesByReport')
    # balance_entries = dd.ShowSlaveTable('sheets.BalanceEntriesByReport')
    # results_entries = dd.ShowSlaveTable('sheets.ResultsEntriesByReport')

    def __str__(self):
        return "Report #{} ({}..{})".format(self.pk, self.start_period, self.end_period)

    def check_period_range(self):
        if not self.start_period:
            raise Warning(_("Select at least a start period"))
        if self.end_period:
            if str(self.start_period) > str(self.end_period):
                raise Warning(_("End period must be after start period"))

    @classmethod
    def get_certifiable_fields(cls):
        return 'start_period end_period user'

    # def full_clean(self, *args, **kw):
    #     AP = rt.models.ledger.AccountingPeriod
    #     if not self.start_period_id:
    #         self.start_period = AP.get_default_for_date(dd.today())
    #     super(Report, self).full_clean(*args, **kw)

    def get_outer_queryset(self, coll):
        """
        Return the filtered queryset over the rows to show in this
        report using the given collector.

        Each row is annotated with the fields old_d, old_c, during_d and during_c.

        Outer objects can be ledger or analytical accounts, partners or sheet
        items.

        """
        # see https://docs.djangoproject.com/en/3.1/ref/models/expressions/#using-aggregates-within-a-subquery-expression
        AccountingPeriod = rt.models.ledger.AccountingPeriod
        sp = self.start_period or AccountingPeriod.get_default_for_date(
            dd.today())
        ep = self.end_period or sp
        before_periods = AccountingPeriod.objects.filter(
            ref__lt=sp.ref)
        during_periods = AccountingPeriod.objects.filter(
            ref__gte=sp.ref, ref__lte=ep.ref)

        oldflt = coll.get_mvt_filter()
        duringflt = coll.get_mvt_filter()
        oldflt.update(voucher__accounting_period__in=before_periods)
        duringflt.update(voucher__accounting_period__in=during_periods)

        kw = dict()
        coll.addann(kw, 'old_d', DC.debit, oldflt)
        coll.addann(kw, 'old_c', DC.credit, oldflt)
        coll.addann(kw, 'during_d', DC.debit, duringflt)
        coll.addann(kw, 'during_c', DC.credit, duringflt)

        qs = coll.outer_model.objects.annotate(**kw)
        qs = qs.exclude(old_d=ZERO, old_c=ZERO, during_d=ZERO, during_c=ZERO)
        # print("20201013d {}".format(qs.query))
        return qs

    def get_entry_models(self):
        yield AccountEntry
        yield PartnerEntry
        if dd.is_installed('ana'):
            yield AnaAccountEntry
        if dd.is_installed('sheets'):
            yield ItemEntry

    def reset_plan(self):
        for em in self.get_entry_models():
            em.objects.filter(report=self).delete()

    def run_update_plan(self, ar):
        self.check_period_range()
        for em in self.get_entry_models():
            em.objects.filter(report=self).delete()
            for coll in em.get_collectors():
                for obj in self.get_outer_queryset(coll):
                    entry = coll.create_entry(self, obj)
                    entry.full_clean()
                    entry.save()
                    # try:
                    #     entry.full_clean()
                    #     entry.save()
                    # except Exception as e:
                    #     print("20200926 failed to save {} : {}".format(entry, e))
                # coll.compute_sums(self)
            em.compute_sum_entries(self)

        # TODO: compute net income/loss or not?
        # nil = CommonItems.net_income_loss.get_object()
        # if collector[nil.ref].value == ZERO:
        #     net_income = ZERO
        #     for entry in collector.values():
        #         if entry.value:
        #             if entry.item.sheet_type == SheetTypes.results:
        #                 if entry.item.dc == nil.dc:
        #                     net_income += entry.value
        #                 else:
        #                     net_income -= entry.value
        #     if net_income > 0:
        #         collector[nil.ref].value = net_income
        #         e = collector[CommonItems.net_income.value]
        #         assert e.value == ZERO
        #         e.value = net_income
        #     elif net_income < 0:
        #         collector[nil.ref].value = net_income
        #         e = collector[CommonItems.net_loss.value]
        #         assert e.value == ZERO
        #         e.value = - net_income


    def get_story(self, ar, header_level=None):
        self.check_period_range()
        yield AccountEntriesByReport.request(self, parent=ar)
        if dd.is_installed('ana'):
            yield AnaAccountEntriesByReport.request(self, parent=ar)
        for tt in TradeTypes.get_list_items():
            yield PartnerEntriesByReport.request(self, parent=ar,
                param_values=dict(trade_type=tt))
        yield BalanceEntriesByReport.request(self, parent=ar)
        yield ResultsEntriesByReport.request(self, parent=ar)

dd.update_field(Report, 'start_period', null=True)


class Items(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.Item'
    order_by = ['ref']
    column_names = "ref designation sheet_type dc common_item *"


class AccountEntries(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.AccountEntry'
    order_by = ['account__ref']

class PartnerEntries(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.PartnerEntry'
    order_by = ['partner__name']

class AnaAccountEntries(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.AnaAccountEntry'
    order_by = ['ana_account__ref']


class ItemEntries(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.ItemEntry'
    order_by = ['item__ref']
    column_names = "description:40 old_d old_c during_d during_c report *"
    detail_layout = """
    report item old_d old_c during_d during_c
    MovementsByItemEntry
    """
    sheet_type = None
    hide_sums = True

    @classmethod
    def get_title(cls, ar):
        if cls.sheet_type is None:
            return super(ItemEntries, cls).get_title(ar)
        return str(cls.sheet_type.text)
        # return str(ar.param_values.sheet_type.text)

    @classmethod
    def get_request_queryset(cls, ar):
        # if ar is None:
        #     return cls.model.objects.none()
        # mi = ar.master_instance
        # if mi is None:
        #     return cls.model.objects.none()
        qs = super(ItemEntries, cls).get_request_queryset(ar)
        if cls.sheet_type is not None:
            qs = qs.filter(item__sheet_type=cls.sheet_type)
        return qs


class EntriesByReport(dd.Table):
    # hide_sums = True
    master_key = 'report'
    # column_names = "description:40 old_d old_c during_d during_c new_d new_c"
    column_names = "description:40 old_dc during_d during_c new_dc *"
    details_of_master_template = _("%(details)s")


class AccountEntriesByReport(AccountEntries, EntriesByReport):
    pass

class PartnerEntriesByReport(PartnerEntries, EntriesByReport):
    pass

class AnaAccountEntriesByReport(AnaAccountEntries, EntriesByReport):
    pass

class BalanceEntriesByReport(ItemEntries, EntriesByReport):
    column_names = "description:40 activa passiva"
    sheet_type = SheetTypes.balance

class ResultsEntriesByReport(ItemEntries, EntriesByReport):
    column_names = "description:40 expenses revenues"
    sheet_type = SheetTypes.results


# class ReportDetail(dd.DetailLayout):
#     main = "first #second AnaAccountEntriesByReport ItemEntriesByReport"

#     first = dd.Panel("""
#     start_period end_period printed
#     AccountEntriesByReport
#     """, label=_("First"))

#     # second = dd.Panel("""
#     # PartnerEntriesByReport
#     # """, label=_("Second"))

class Reports(dd.Table):
    model = 'sheets.Report'
    # detail_layout = 'ledger.ReportDetail'
    detail_layout = """
    start_period end_period printed
    body
    """


from lino_xl.lib.ledger.ui import Movements

class MovementsByItemEntry(Movements):
    master = 'sheets.ItemEntry'

    @classmethod
    def get_request_queryset(cls, ar):
        if ar is None:
            return cls.model.objects.none()
        mi = ar.master_instance
        if mi is None:
            return cls.model.objects.none()
        qs = super(MovementsByItemEntry, cls).get_request_queryset(ar)
        qs = qs.filter(account__sheet_item=mi.item)
        return qs

# class Reports(dd.Table):
#     required_roles = dd.login_required(LedgerUser)
#     model = 'sheets.Report'
#     detail_layout = 'sheets.ReportDetail'

# class ReportsByJournal(ByJournal, Reports):
#     master_key = 'journal'
#     insert_layout = """
#     entry_date user
#     start_period end_period
#     """

# VoucherTypes.add_item_lazy(ReportsByJournal)
