# -*- coding: UTF-8 -*-
# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
from builtins import str

import datetime

from django.db import models
from django.db.models.functions import Length

from etgen.html import E

from lino.api import dd, rt, _
from lino.mixins import Referrable
from lino_xl.lib.excerpts.mixins import Certifiable
from lino.utils.mldbc.mixins import BabelDesignated
from lino_xl.lib.ledger.models import DebitOrCreditField
from lino_xl.lib.ledger.utils import DEBIT, CREDIT, ZERO
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.mixins import SequencedVoucherItem
from lino_xl.lib.ledger.mixins import PeriodRange
from lino.modlib.system.choicelists import PeriodEvents
from lino.modlib.summaries.mixins import SimpleSummary
from lino_xl.lib.ledger.ui import ByJournal
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff

from .choicelists import SheetTypes, CommonItems

DEMO_JOURNAL_NAME = "BAL"

class Item(BabelDesignated, Referrable):
    class Meta:
        app_label = 'sheets'
        verbose_name = _("Sheet item")
        verbose_name_plural = _("Sheet items")
        abstract = dd.is_abstract_model(__name__, 'Item')

    ref_max_length = dd.plugins.sheets.ref_length
    
    dc = DebitOrCreditField(_("Booking direction"))
    sheet_type = SheetTypes.field()
    common_item = CommonItems.field(blank=True)
    mirror_ref = models.CharField()
    mirror_ref = models.CharField(
        _("Mirror"), max_length=ref_max_length,
        blank=True, null=True)

    @classmethod
    def get_usable_items(cls):
        return cls.objects.annotate(
            ref_len=Length('ref')).filter(
                ref_len=dd.plugins.sheets.ref_length)
    
    def get_choices_text(self, request, actor, field):
        return "{} {}".format(self.ref, self)

    def is_heading(self):
        return len(self.ref) < dd.plugins.sheets.ref_length


class Entry(SimpleSummary):
    
    class Meta:
        app_label = 'sheets'
        abstract = dd.is_abstract_model(__name__, 'Entry')
        verbose_name = _("Sheet entry")
        verbose_name_plural = _("Sheet entries")

    show_in_site_search = False
    
    master = dd.ForeignKey('ledger.FiscalYear')
    item = dd.ForeignKey('sheets.Item')
    value = dd.PriceField(_("Value"))

    @classmethod
    def update_for_master(cls, master):
        # a custom update_for_master because here we have multiple
        # summary objects per master.
        
        cls.objects.filter(master=master).delete()

        collector = {}
        sums = {}
        
        for i in rt.models.sheets.Item.objects.all():
            obj = cls(item=i, master=master, value=ZERO)
            if len(i.ref) == dd.plugins.sheets.ref_length:
                collector[i.ref] = obj
            else:
                sums[i.ref] = obj

        # from django.db.models import Q, Sum
        # debits = qs.aggregate(debit=Sum('amount', filter=Q(dc=DEBIT)))
        # credits = qs.aggregate(credit=Sum('amount', filter=Q(dc=CREDIT)))

        qs = rt.models.ledger.Movement.objects.filter(
            voucher__accounting_period__year=master)
        for mvt in qs:
            item = mvt.account.sheet_item
            entry = collector[item.ref]
            if mvt.dc == item.dc:
                entry.value += mvt.amount
            else:
                entry.value -= mvt.amount

        nil = CommonItems.net_income_loss.get_object()
        if collector[nil.ref].value == ZERO:
            net_income = ZERO
            for entry in collector.values():
                if entry.value:
                    if entry.item.sheet_type == SheetTypes.results:
                        if entry.item.dc == nil.dc:
                            net_income += entry.value
                        else:
                            net_income -= entry.value
            if net_income > 0:
                collector[nil.ref].value = net_income
                e = collector[CommonItems.net_income.value]
                assert e.value == ZERO
                e.value = net_income
            elif net_income < 0:
                collector[nil.ref].value = net_income
                e = collector[CommonItems.net_loss.value]
                assert e.value == ZERO
                e.value = - net_income
        
        for entry in collector.values():
            mr = entry.item.mirror_ref
            if mr and entry.value < 0:
                me = collector[mr]
                if me.value:
                    raise Exception("20180828 {} {}".format(
                        entry.item.ref, me.item.ref))
                me.value = - obj.value
                entry.value = 0
                # obj.item = rt.models.sheets.Item.objects.get(ref=mr)
                    
        for entry in collector.values():
            ref = entry.item.ref[:-1]
            while len(ref) > 0:
                se = sums.get(ref, None)
                if se is not None:
                    if se.item.dc == entry.item.dc:
                        se.value += entry.value
                    else:
                        se.value -= entry.value
                else:
                    # ignore sums for which there is no item
                    pass
                ref = ref[:-1]

        for entry in collector.values() + sums.values():
            if entry.value:
                entry.full_clean()
                entry.save()
            
    def value2html(self, ar):
        txt = dd.format_currency(self.value, False, True)
        if self.item.is_heading():
            # return E.b(txt)
            return E.div(E.b(txt), align="right")
        # return txt
        return E.div(txt, align="right")
    
    @dd.displayfield(_("Activa"), max_length=12)
    def activa(self, ar):
        if self.item.dc:
            return self.value2html(ar)

    @dd.displayfield(_("Passiva"), max_length=12)
    def passiva(self, ar):
        if not self.item.dc:
            return self.value2html(ar)

    @dd.displayfield(_("Expenses"), max_length=12)
    def expenses(self, ar):
        if not self.item.dc:
            return self.value2html(ar)

    @dd.displayfield(_("Revenues"), max_length=12)
    def revenues(self, ar):
        if self.item.dc:
            return self.value2html(ar)

    # @dd.displayfield(max_length=dd.plugins.sheets.ref_length*2)
    # def item_ref(self, ar):
    #     ref = self.item.ref
    #     ref = u' ' * (len(ref)-1) + ref
    #     return ref

    @dd.displayfield(_("Description"), max_length=50)
    def description(self, ar):
        s = self.item.ref
        s = u' ' * (len(s)-1) + s
        s += " " + str(self.item)
        if self.item.is_heading():
            s = E.b(s)
        return s
    
Entry.set_widget_options('value', hide_sum=True)

        
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

class Entries(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = 'sheets.Entry'
    detail_layout = """
    master item value
    MovementsByEntry
    """
    order_by = ['master', 'item__ref']
    column_names = 'master item item__dc value'

class BalanceByYear(Entries):
    label = SheetTypes.balance.text
    master_key = 'master'
    # order_by = ['item__ref']
    # column_names = 'item_ref item activa passiva'
    column_names = 'description activa passiva'
    filter = models.Q(item__sheet_type=SheetTypes.balance)

class ResultsByYear(Entries):
    label = SheetTypes.results.text
    master_key = 'master'
    # order_by = ['item__ref']
    # column_names = 'item_ref item expenses revenues'
    column_names = 'description expenses revenues'
    filter = models.Q(item__sheet_type=SheetTypes.results)

    
from lino_xl.lib.ledger.ui import Movements

class MovementsByEntry(Movements):
    master = 'sheets.Entry'
    @classmethod
    def get_request_queryset(cls, ar):
        qs = super(MovementsByEntry, cls).get_request_queryset(ar)
        if ar is None:
            return cls.model.objects.none()
        mi = ar.master_instance
        if mi is None:
            return cls.model.objects.none()
        # assert isinstance(mi.master, rt.models.ledger.FiscalYear)
        print("20180828 {} {}".format(mi.item, mi.master))
        qs = qs.filter(
            account__sheet_item=mi.item,
            voucher__accounting_period__year=mi.master)
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

