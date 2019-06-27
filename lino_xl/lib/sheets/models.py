# -*- coding: UTF-8 -*-
# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
from builtins import str

# import datetime

from django.db import models
from django.db.models import OuterRef, Subquery, Sum

from etgen.html import E

from lino.api import dd, rt, _
from lino.mixins import StructuredReferrable, Story
from lino_xl.lib.excerpts.mixins import Certifiable
from lino.utils.mldbc.mixins import BabelDesignated
from lino_xl.lib.ledger.models import DebitOrCreditField
from lino_xl.lib.ledger.utils import DEBIT, CREDIT, ZERO, Balance,myround
from lino_xl.lib.ledger.choicelists import TradeTypes
#from lino_xl.lib.ledger.models import Voucher
#from lino_xl.lib.ledger.mixins import SequencedVoucherItem
from lino_xl.lib.ledger.mixins import PeriodRange
#from lino.modlib.system.choicelists import PeriodEvents
#from lino.modlib.summaries.mixins import SimpleSummary
#from lino_xl.lib.ledger.ui import ByJournal
from lino.modlib.users.mixins import UserPlan
from lino_xl.lib.ledger.roles import LedgerStaff

from .choicelists import SheetTypes, CommonItems

# DEMO_JOURNAL_NAME = "BAL"

class Item(StructuredReferrable, BabelDesignated):
    class Meta:
        app_label = 'sheets'
        verbose_name = _("Sheet item")
        verbose_name_plural = _("Sheet items")
        abstract = dd.is_abstract_model(__name__, 'Item')

    ref_max_length = dd.plugins.sheets.item_ref_width

    dc = DebitOrCreditField(_("Booking direction"))
    sheet_type = SheetTypes.field()
    common_item = CommonItems.field(blank=True)
    mirror_ref = models.CharField(
        _("Mirror"), max_length=ref_max_length,
        blank=True, null=True)


class Collector(object):
    def __init__(self, model, fkname, outer_link, **rowmvtfilter):
        self.entry_model = model
        self.rowmvtfilter = rowmvtfilter
        self.rowmvtfilter[outer_link] = OuterRef('pk')
        self.fkname = fkname
        self.fk = model._meta.get_field(fkname)
        self.outer_model = self.fk.remote_field.model
        self.outer_link = outer_link
        # self.outer_link = self.outer_model._meta.model_name
        # print(20180905, self.outer_link)

    def get_mvt_filter(self, **flt):
        flt.update(self.rowmvtfilter)
        return flt

    def addann(self, kw, name, dc, flt):
        mvts = rt.models.ledger.Movement.objects.filter(dc=dc, **flt)
        mvts = mvts.order_by()
        mvts = mvts.values(self.outer_link)  # this was the important thing
        mvts = mvts.annotate(total=Sum(
            'amount', output_field=dd.PriceField(decimal_places=14)))# For Django2 we need to set decimal_places to 14 which is the max of decimal_places used in ReportEntry fields.
        mvts = mvts.values('total')
        kw[name] = Subquery(mvts, output_field=dd.PriceField(decimal_places=14))

    def create_entry(self, report, obj, **kwargs):
        kwargs.update(report=report)
        kwargs[self.fkname] = obj
        old = Balance(obj.old_d, obj.old_c)
        kwargs.update(old_d = old.d)
        kwargs.update(old_c = old.c)
        kwargs.update(during_d = myround(obj.during_d or ZERO)) #In Django2, does not respect the decimal_places for the output_field in the aggregation functions.
        kwargs.update(during_c = myround(obj.during_c or ZERO))
        return self.entry_model(**kwargs)

    def compute_sums(self, report):
        collect = []
        k = self.fkname + '__ref__startswith'
        for obj in self.outer_model.get_heading_objects():
            qs = self.entry_model.objects.filter(**{k: obj.ref})
            kw = dict()
            kw.update(old_d=models.Sum('old_d'))
            kw.update(old_c=models.Sum('old_c'))
            kw.update(during_d=models.Sum('during_d'))
            kw.update(during_c=models.Sum('during_c'))
            d = qs.aggregate(**kw)
            if d['old_d'] or d['old_c'] or d['during_d'] or d['during_c']:
                if d['during_d']:
                    d['during_d'] = myround(d['during_d'])
                if d['during_c']:
                    d['during_c'] = myround(d['during_c'])
                d['report'] = report
                d[self.fkname] = obj
                collect.append(self.entry_model(**d))
                # print(20180905, d)

        for obj in collect:
            obj.full_clean()
            obj.save()


class TradeTypeCollector(Collector):
    def __init__(self, tt, *args, **kwargs):
        self.trade_type = tt
        super(TradeTypeCollector, self).__init__(*args, **kwargs)

    def create_entry(self, *args, **kwargs):
        kwargs.update(trade_type=self.trade_type)
        return super(TradeTypeCollector, self).create_entry(*args, **kwargs)

    def compute_sums(self, report):
        pass


class ReportEntry(dd.Model):
    class Meta:
        abstract = True

    show_in_site_search = False

    report = dd.ForeignKey('sheets.Report')
    old_d = dd.PriceField(_("Debit before"), 14, null=True, blank=True)
    old_c = dd.PriceField(_("Credit before"), 14, null=True, blank=True)
    during_d = dd.PriceField(_("Debit"), 14, null=True, blank=True)
    during_c = dd.PriceField(_("Credit"), 14, null=True, blank=True)

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


class AccountEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'AccountEntry')
        verbose_name = _("General account balance")
        verbose_name_plural = _("General account balances")

    allow_cascaded_delete = ['account']

    account = dd.ForeignKey('ledger.Account')

    @dd.displayfield(_("Description"))
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

    allow_cascaded_delete = ['partner']

    partner = dd.ForeignKey('contacts.Partner')
    trade_type = TradeTypes.field()

    @dd.displayfield(_("Description"))
    def description(self, ar=None):
        if ar is None:
            return str(self.partner)
        return self.partner.obj2href(ar)

    @classmethod
    def get_collectors(cls):
        for tt in TradeTypes.get_list_items():
            a = tt.get_main_account()
            yield TradeTypeCollector(
                tt, cls, 'partner', 'partner', account=a)

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

    allow_cascaded_delete = ['item']

    item = dd.ForeignKey('sheets.Item')

    @dd.displayfield(_("Description"))
    def description(self, ar=None):
        # print(20180831, ar.renderer, ar.user)
        return self.item.description

    @classmethod
    def get_collectors(cls):
        yield Collector(cls, 'item', 'account__sheet_item')

    @classmethod
    def setup_parameters(cls, fields):
        fields.setdefault(
            'sheet_type', SheetTypes.field())
        super(ItemEntry, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(self, ar, **filter):
        qs = super(ItemEntry, self).get_request_queryset(ar, **filter)
        pv = ar.param_values
        if pv.sheet_type:
            qs = qs.filter(item__sheet_type=pv.sheet_type)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(ItemEntry, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.sheet_type:
            yield str(pv.sheet_type)

    @dd.virtualfield(dd.PriceField(_("Activa")))
    def activa(self, ar):
        if self.item.dc is CREDIT:
            return self.new_balance().c

    @dd.virtualfield(dd.PriceField(_("Passiva")))
    def passiva(self, ar):
        if self.item.dc is DEBIT:
            return self.new_balance().d

    # @dd.displayfield(_("Activa"), max_length=12)
    # def activa(self, ar):
    #     if self.item.dc:
    #         return self.value2html(ar)

    # @dd.displayfield(_("Passiva"), max_length=12)
    # def passiva(self, ar):
    #     if not self.item.dc:
    #         return self.value2html(ar)

    @dd.virtualfield(dd.PriceField(_("Expenses")))
    def expenses(self, ar):
        if self.item.dc is DEBIT:
            return self.new_balance().d

    @dd.virtualfield(dd.PriceField(_("Revenues")))
    def revenues(self, ar):
        if self.item.dc is CREDIT:
            return self.new_balance().c


class AnaAccountEntry(ReportEntry):
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'AnaAccountEntry')
        verbose_name = _("Analytic account balance")
        verbose_name_plural = _("Analytic account balances")

    ana_account = dd.ForeignKey('ana.Account')

    @dd.displayfield(_("Description"))
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

    def get_balances_queryset(self, coll):
        # see https://docs.djangoproject.com/en/1.11/ref/models/expressions/#using-aggregates-within-a-subquery-expression
        AccountingPeriod = rt.models.ledger.AccountingPeriod
        sp = self.start_period or AccountingPeriod.get_default_for_date(
            dd.today())
        ep = self.end_period or sp

        qs = coll.outer_model.objects.all()

        during_periods = AccountingPeriod.objects.filter(
            ref__gte=sp.ref, ref__lte=ep.ref)
        before_periods = AccountingPeriod.objects.filter(
            ref__lt=sp.ref)

        oldflt = coll.get_mvt_filter()
        duringflt = coll.get_mvt_filter()
        # oldflt = dict()
        # oldflt.update(coll.rowmvtflt)
        # duringflt = dict()
        # duringflt.update(coll.rowmvtflt)
        oldflt.update(voucher__accounting_period__in=before_periods)
        duringflt.update(voucher__accounting_period__in=during_periods)

        kw = dict()
        coll.addann(kw, 'old_d', DEBIT, oldflt)
        coll.addann(kw, 'old_c', CREDIT, oldflt)
        coll.addann(kw, 'during_d', DEBIT, duringflt)
        coll.addann(kw, 'during_c', CREDIT, duringflt)

        qs = qs.annotate(**kw)

        qs = qs.exclude(
            old_d=ZERO, old_c=ZERO,
            during_d=ZERO, during_c=ZERO)

        # print("20170930 {}".format(qs.query))
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
                for obj in self.get_balances_queryset(coll):
                    entry = coll.create_entry(self, obj)
                    try:
                        entry.full_clean()
                        entry.save()
                    except Exception:
                        self.get_balances_queryset(coll)
                coll.compute_sums(self)

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
        # if header_level is None:
        #     header = None
        #     header = getattr(E, "h{}".format(header_level))
        # pv = ar.param_values
        self.check_period_range()
        # bpv = dict(start_period=self.start_period,
        #            end_period=self.end_period)
        balances = []
        if True:
            balances.append(ar.spawn(
                AccountEntriesByReport, master_instance=self))
        if dd.is_installed('ana'):
            balances.append(ar.spawn(
                AnaEntriesByReport, master_instance=self))
        for tt in TradeTypes.get_list_items():
            balances.append(ar.spawn(
                PartnerEntriesByReport,
                master_instance=self,
                param_values=dict(trade_type=tt)))
        balances.append(ar.spawn(
            BalanceEntriesByReport,
            master_instance=self,
            param_values=dict(sheet_type=SheetTypes.balance)))
        balances.append(ar.spawn(
            ResultsEntriesByReport,
            master_instance=self,
            param_values=dict(sheet_type=SheetTypes.results)))

        # for st in SheetTypes.get_list_items():
        #     balances.append(ar.spawn(
        #         ItemEntriesByReport,
        #         master_instance=self,
        #         param_values=dict(sheet_type=st)))

        if True:
            for sar in balances:
                # if header:
                #     yield header(str(sar.get_title()))
                yield sar

dd.update_field(Report, 'start_period', null=True)


# class Entry(SimpleSummary):

#     class Meta:
#         app_label = 'sheets'
#         abstract = dd.is_abstract_model(__name__, 'Entry')
#         verbose_name = _("Sheet entry")
#         verbose_name_plural = _("Sheet entries")

#     show_in_site_search = False

#     master = dd.ForeignKey('ledger.FiscalYear')
#     item = dd.ForeignKey('sheets.Item')
#     value = dd.PriceField(_("Value"))

#     @classmethod
#     def update_for_master(cls, master):
#         # a custom update_for_master because here we have multiple
#         # summary objects per master.

#         cls.objects.filter(master=master).delete()

#         collector = {}
#         sums = {}

#         for i in rt.models.sheets.Item.objects.all():
#             obj = cls(item=i, master=master, value=ZERO)
#             if len(i.ref) == dd.plugins.sheets.ref_length:
#                 collector[i.ref] = obj
#             else:
#                 sums[i.ref] = obj

#         # from django.db.models import Q, Sum
#         # debits = qs.aggregate(debit=Sum('amount', filter=Q(dc=DEBIT)))
#         # credits = qs.aggregate(credit=Sum('amount', filter=Q(dc=CREDIT)))

#         qs = rt.models.ledger.Movement.objects.filter(
#             voucher__accounting_period__year=master)
#         for mvt in qs:
#             item = mvt.account.sheet_item
#             entry = collector[item.ref]
#             if mvt.dc == item.dc:
#                 entry.value += mvt.amount
#             else:
#                 entry.value -= mvt.amount

#         nil = CommonItems.net_income_loss.get_object()
#         if collector[nil.ref].value == ZERO:
#             net_income = ZERO
#             for entry in collector.values():
#                 if entry.value:
#                     if entry.item.sheet_type == SheetTypes.results:
#                         if entry.item.dc == nil.dc:
#                             net_income += entry.value
#                         else:
#                             net_income -= entry.value
#             if net_income > 0:
#                 collector[nil.ref].value = net_income
#                 e = collector[CommonItems.net_income.value]
#                 assert e.value == ZERO
#                 e.value = net_income
#             elif net_income < 0:
#                 collector[nil.ref].value = net_income
#                 e = collector[CommonItems.net_loss.value]
#                 assert e.value == ZERO
#                 e.value = - net_income

#         for entry in collector.values():
#             mr = entry.item.mirror_ref
#             if mr and entry.value < 0:
#                 me = collector[mr]
#                 if me.value:
#                     raise Exception("20180828 {} {}".format(
#                         entry.item.ref, me.item.ref))
#                 me.value = - obj.value
#                 entry.value = 0
#                 # obj.item = rt.models.sheets.Item.objects.get(ref=mr)

#         for entry in collector.values():
#             ref = entry.item.ref[:-1]
#             while len(ref) > 0:
#                 se = sums.get(ref, None)
#                 if se is not None:
#                     if se.item.dc == entry.item.dc:
#                         se.value += entry.value
#                     else:
#                         se.value -= entry.value
#                 else:
#                     # ignore sums for which there is no item
#                     pass
#                 ref = ref[:-1]
#         for entry in list(collector.values()) + list(sums.values()):
#             if entry.value:
#                 entry.full_clean()
#                 entry.save()

#     def value2html(self, ar):
#         txt = dd.format_currency(self.value, False, True)
#         if self.item.is_heading():
#             # return E.b(txt)
#             return E.div(E.b(txt), align="right")
#         # return txt
#         return E.div(txt, align="right")

#     @dd.displayfield(_("Activa"), max_length=12)
#     def activa(self, ar):
#         if self.item.dc:
#             return self.value2html(ar)

#     @dd.displayfield(_("Passiva"), max_length=12)
#     def passiva(self, ar):
#         if not self.item.dc:
#             return self.value2html(ar)

#     @dd.displayfield(_("Expenses"), max_length=12)
#     def expenses(self, ar):
#         if not self.item.dc:
#             return self.value2html(ar)

#     @dd.displayfield(_("Revenues"), max_length=12)
#     def revenues(self, ar):
#         if self.item.dc:
#             return self.value2html(ar)

#     # @dd.displayfield(max_length=dd.plugins.sheets.ref_length*2)
#     # def item_ref(self, ar):
#     #     ref = self.item.ref
#     #     ref = u' ' * (len(ref)-1) + ref
#     #     return ref

# Entry.set_widget_options('value', hide_sum=True)


# class ReportDetail(dd.DetailLayout):
#     main = "general ledger"

#     general = dd.Panel("""
#     number entry_date 
#     start_period end_period
#     workflow_buttons user
#     EntriesByReport
#     """, label=_("General"))

#     ledger = dd.Panel("""
#     journal accounting_period id narration
#     ledger.MovementsByVoucher
#     """, label=_("Ledger"))




class Items(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.Item'
    order_by = ['ref']
    column_names = "ref designation sheet_type dc common_item *"

# class ItemEntries(dd.Table):
#     required_roles = dd.login_required(LedgerStaff)
#     model = 'sheets.ItemEntry'
#     detail_layout = """
#     report item old_d old_c during_d during_c
#     MovementsByItemEntry
#     """
#     order_by = ['report', 'item__ref']
#     column_names = 'report item *'

# class BalanceByYear(Entries):
#     label = SheetTypes.balance.text
#     master_key = 'master'
#     # order_by = ['item__ref']
#     # column_names = 'item_ref item activa passiva'
#     column_names = 'item__description activa passiva'
#     filter = models.Q(item__sheet_type=SheetTypes.balance)

# class ResultsByYear(Entries):
#     label = SheetTypes.results.text
#     master_key = 'master'
#     # order_by = ['item__ref']
#     # column_names = 'item_ref item expenses revenues'
#     column_names = 'item__description expenses revenues'
#     filter = models.Q(item__sheet_type=SheetTypes.results)


from lino_xl.lib.ledger.ui import Movements

class EntriesByReport(dd.Table):
    hide_sums = True
    master_key = 'report'
    column_names = "description:40 old_d old_c during_d during_c new_c new_d"
    details_of_master_template = _("%(details)s")

class AccountEntriesByReport(EntriesByReport):
    model = 'sheets.AccountEntry'
    order_by = ['account__ref']

class PartnerEntriesByReport(EntriesByReport):
    model = 'sheets.PartnerEntry'
    order_by = ['partner__name']

class AnaAcountEntries(dd.Table):
    model = 'sheets.AnaAccountEntry'
    order_by = ['ana_account__ref']

class AnaEntriesByReport(AnaAcountEntries, EntriesByReport):
    pass

class ItemEntriesByReport(EntriesByReport):
    model = 'sheets.ItemEntry'
    order_by = ['item__ref']
    detail_layout = """
    report item old_d old_c during_d during_c
    MovementsByItemEntry
    """

    @classmethod
    def get_title(self, ar):
        return str(ar.param_values.sheet_type.text)

class BalanceEntriesByReport(ItemEntriesByReport):
    column_names = "description:40 activa passiva"

class ResultsEntriesByReport(ItemEntriesByReport):
    column_names = "description:40 expenses revenues"


# class ReportDetail(dd.DetailLayout):
#     main = "first #second AnaEntriesByReport ItemEntriesByReport"

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


# class MovementsByItem(Movements):
#     master_key = 'account__sheet_item'

class MovementsByItemEntry(Movements):
    master = 'sheets.ItemEntry'
    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(MovementsByItemEntry, cls).get_request_queryset(ar)
        if ar is None:
            return cls.model.objects.none()
        mi = ar.master_instance
        if mi is None:
            return cls.model.objects.none()
        # assert isinstance(mi.master, rt.models.ledger.FiscalYear)
        # print("20180828 {} {}".format(mi.item, mi.master))
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

