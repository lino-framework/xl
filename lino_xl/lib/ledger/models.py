# -*- coding: UTF-8 -*-
# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from lino.utils import last_day_of_month
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.dispatch import Signal
from django.utils.text import format_lazy

from lino.api import _
from lino.mixins import BabelNamed, Sequenced, StructuredReferrable, Referrable
from lino.utils.mldbc.mixins import BabelDesignated
from lino.mixins.periods import DateRange
from lino.mixins.duplicable import Duplicable
from lino.mixins.registrable import Registrable
from lino.modlib.checkdata.choicelists import Checker
from lino.modlib.printing.mixins import PrintableType
from lino.modlib.system.choicelists import ObservedEvent
from lino.modlib.uploads.mixins import UploadController
from lino.modlib.users.mixins import UserAuthored
from lino.core.fields import TableRow
from lino.utils import SumCollector
from lino.utils import mti
from lino_xl.lib.contacts.choicelists import PartnerEvents
from lino_xl.lib.vat.choicelists import VatClasses, VatColumns
from lino_xl.lib.excerpts.mixins import Certifiable

from .utils import myround
from .choicelists import CommonAccounts
from .choicelists import DC, PeriodStates
from .mixins import ProjectRelated, VoucherNumber, PeriodRange, PeriodRangeObservable, Payable
from .roles import VoucherSupervisor
from .ui import *


class LedgerInfo(dd.Model):
    class Meta:
        app_label = 'ledger'

    allow_cascaded_delete = 'user'
    user = dd.OneToOneField('users.User', primary_key=True)
    entry_date = models.DateField(
        _("Last entry date"), null=True, blank=True)

    @classmethod
    def get_for_user(cls, user):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            return cls(user=user)


class Journal(BabelNamed, Sequenced, Referrable, PrintableType):

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")

    ref_max_length = 5

    trade_type = TradeTypes.field(blank=True)
    voucher_type = VoucherTypes.field()
    journal_group = JournalGroups.field()
    auto_check_clearings = models.BooleanField(
        _("Check clearing"), default=True)
    auto_fill_suggestions = models.BooleanField(
        _("Fill suggestions"), default=True)
    force_sequence = models.BooleanField(
        _("Force chronological sequence"), default=False)
    preliminary = models.BooleanField(_("Preliminary"), default=False)

    account = dd.ForeignKey('ledger.Account', blank=True, null=True)
    partner = dd.ForeignKey('contacts.Company', blank=True, null=True)
    printed_name = dd.BabelCharField(
        _("Printed document designation"), max_length=100, blank=True)
    dc = DC.field(_("Primary booking direction"), blank=True, null=True)
    # dc = DebitOrCreditField(_("Primary booking direction"))
    yearly_numbering = models.BooleanField(
        _("Yearly numbering"), default=True)
    must_declare = models.BooleanField(default=True)
    uploads_volume = dd.ForeignKey("uploads.Volume", blank=True, null=True)
    # invert_due_dc = models.BooleanField(
    #     _("Invert booking direction"),
    #     help_text=_("Whether to invert booking direction of due movement."),
    #     default=True)

    def get_doc_model(self):
        """The model of vouchers in this Journal.

        """
        # print self,DOCTYPE_CLASSES, self.doctype
        return self.voucher_type.model
        #~ return DOCTYPES[self.doctype][0]

    def get_doc_report(self):
        return self.voucher_type.table_class
        #~ return DOCTYPES[self.doctype][1]

    def get_voucher(self, year=None, number=None, **kw):
        cl = self.get_doc_model()
        kw.update(journal=self, accounting_period__year=year, number=number)
        return cl.objects.get(**kw)

    def create_voucher(self, **kw):
        """Create a voucher in this journal.

        """
        cl = self.get_doc_model()
        kw.update(journal=self)
        doc = cl()
        # doc = cl(**kw) # wouldn't work. See Django ticket #10808
        for k, v in kw.items():
            setattr(doc, k, v)
        # try:
        #     doc = cl()
        #     # doc = cl(**kw) # wouldn't work. See Django ticket #10808
        #     for k, v in kw.items():
        #         setattr(doc, k, v)
        #     #~ print 20120825, kw
        # except TypeError:
        #     #~ print 20100804, cl
        #     raise
        doc.on_create(None)
        #~ doc.full_clean()
        #~ doc.save()
        return doc

    def get_allowed_accounts(self, **kw):
        if self.trade_type:
            return self.trade_type.get_allowed_accounts(**kw)
        # kw.update(chart=self.chart)
        return rt.models.ledger.Account.objects.filter(**kw)

    def get_next_number(self, voucher):
        # ~ self.save() # 20131005 why was this?
        cl = self.get_doc_model()
        assert voucher.journal == self
        assert cl is voucher.__class__
        qs = cl.objects.filter(journal=self)
        if self.yearly_numbering:
            qs = qs.filter(accounting_period__year=voucher.accounting_period.year)
        if voucher.pk:
            # after editing the entry_date of the last voucher of the journal we
            # don't want its number to increase
            qs = qs.exclude(pk=voucher.pk)
        d = qs.aggregate(models.Max('number'))
        number = d['number__max']
        #~ logger.info("20121206 get_next_number %r",number)
        if number is None:
            return 1
        return number + 1

    def __str__(self):
        # s = super(Journal, self).__str__()
        s = dd.babelattr(self, 'name')
        if self.ref:
            s += " (%s)" % self.ref
            #~ return '%s (%s)' % (d.BabelNamed.__unicode__(self),self.ref or self.id)
        return s
            #~ return self.ref +'%s (%s)' % mixins.BabelNamed.__unicode__(self)
            #~ return self.id +' (%s)' % mixins.BabelNamed.__unicode__(self)

    # def save(self, *args, **kw):
    #     #~ self.before_save()
    #     r = super(Journal, self).save(*args, **kw)
    #     self.after_save()
    #     return r

    def after_ui_save(self, ar, cw):
        super(Journal, self).after_ui_save(ar, cw)
        settings.SITE.kernel.must_build_site_cache()

    # def after_save(self):
    #     pass
    #
    def full_clean(self, *args, **kw):
        if self.dc is None:
            if self.trade_type:
                self.dc = self.trade_type.dc
            # elif self.account:
            #     self.dc = self.account.type.dc
            else:
                self.dc = DC.debit  # cannot be NULL

        if not self.name:
            self.name = self.id
        #~ if not self.pos:
            #~ self.pos = self.__class__.objects.all().count() + 1
        super(Journal, self).full_clean(*args, **kw)

    def disable_voucher_delete(self, doc):
        # print "pre_delete_voucher", doc.number, self.get_next_number()
        if self.force_sequence:
            if doc.number + 1 != self.get_next_number(doc):
                return _("%s is not the last voucher in journal"
                         % str(doc))

    def get_template_groups(self):
        """Here we override the class method by an instance method.  This
        means that we must also override all other methods of
        Printable who call the *class* method.  This is currently only
        :meth:`template_choices`.

        """
        return [self.voucher_type.model.get_template_group()]

    @dd.chooser(simple_values=True)
    def template_choices(cls, build_method, voucher_type):
        # Overrides PrintableType.template_choices to not use the class
        # method `get_template_groups`.

        if not voucher_type:
            return []
        #~ print 20131006, voucher_type
        template_groups = [voucher_type.model.get_template_group()]
        return cls.get_template_choices(build_method, template_groups)

    def insert_voucher_button(self, ar):
        table_class = self.get_doc_report()
        sar = table_class.insert_action.request_from(ar, master_instance=self)
        # print(20170217, sar)
        sar.known_values.update(journal=self)
        # sar.known_values.update(journal=self, user=ar.get_user())
        txt = dd.babelattr(self, 'printed_name')
        # txt = self.voucher_type.model._meta.verbose_name_plural
        btn = sar.ar2button(None, _("New {}").format(txt), icon_name=None)
        # btn.set("style", "padding-left:10px")
        return btn



class AccountingPeriod(DateRange, Referrable):
    class Meta:
        app_label = 'ledger'
        verbose_name = _("Accounting period")
        verbose_name_plural = _("Accounting periods")
        ordering = ['ref']

    preferred_foreignkey_width = 10

    state = PeriodStates.field(default='open')
    year = dd.ForeignKey('ledger.FiscalYear', blank=True, null=True)
    remark = models.CharField(_("Remark"), max_length=250, blank=True)

    @classmethod
    def get_available_periods(cls, entry_date):
        """Return a queryset of periods available for booking."""
        if entry_date is None:  # added 20160531
            entry_date = dd.today()
        fkw = dict(start_date__lte=entry_date, end_date__gte=entry_date)
        return rt.models.ledger.AccountingPeriod.objects.filter(**fkw)

    @classmethod
    def get_ref_for_date(cls, d):
        """Return a text to be used as :attr:`ref` for a new period.

        Alternative implementation for usage on a site with movements
        before year 2000::

            @classmethod
            def get_ref_for_date(cls, d):
                if d.year < 2000:
                    y = str(d.year - 1900)
                elif d.year < 2010:
                    y = "A" + str(d.year - 2000)
                elif d.year < 2020:
                    y = "B" + str(d.year - 2010)
                elif d.year < 2030:
                    y = "C" + str(d.year - 2020)
                return y + "{:0>2}".format(d.month)

        """
        y = FiscalYear.year2ref(d.year)
        return "{}-{:0>2}".format(y, d.month)

        # if dd.plugins.ledger.fix_y2k:
        #     return rt.models.ledger.FiscalYear.from_int(d.year).ref \
        #         + "{:0>2}".format(d.month)

        # return "{0.year}-{0.month:0>2}".format(d)

        # """The template used for building the :attr:`ref` of an
        # :class:`AccountingPeriod`.
        #
        # `Format String Syntax
        # <https://docs.python.org/2/library/string.html#formatstrings>`_
        #
        # """

    @classmethod
    def get_periods_in_range(cls, p1, p2):
        return cls.objects.filter(ref__gte=p1.ref, ref__lte=p2.ref)

    @classmethod
    def get_period_filter(cls, voucher_prefix, p1, p2, **kwargs):
        if p1 is None:
            return kwargs

        # ignore preliminary movements if a start_period is given:
        kwargs[voucher_prefix+"journal__preliminary"] = False

        accounting_period = voucher_prefix + "accounting_period"

        if p2 is None:
            kwargs[accounting_period] = p1
        else:
            periods = cls.get_periods_in_range(p1, p2)
            kwargs[accounting_period+'__in'] = periods
        return kwargs

    @classmethod
    def get_default_for_date(cls, d):
        ref = cls.get_ref_for_date(d)
        obj = rt.models.ledger.AccountingPeriod.get_by_ref(ref, None)
        if obj is None:
            values = dict(start_date=d.replace(day=1))
            values.update(end_date=last_day_of_month(d))
            values.update(ref=ref)
            obj = AccountingPeriod(**values)
            obj.full_clean()
            obj.save()
        return obj

    def full_clean(self, *args, **kwargs):
        if self.start_date is None:
            self.start_date = dd.today().replace(day=1)
        if not self.year:
            self.year = FiscalYear.get_or_create_from_date(
                self.start_date)
        super(AccountingPeriod, self).full_clean(*args, **kwargs)

    def __str__(self):
        if not self.ref:
            return dd.obj2str(self)
            # "{0} {1} (#{0})".format(self.pk, self.year)
        return self.ref

AccountingPeriod.set_widget_options('ref', width=6)



class FiscalYear(DateRange, Referrable):

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Fiscal year")
        verbose_name_plural = _("Fiscal years")
        ordering = ['ref']

    preferred_foreignkey_width = 10

    state = PeriodStates.field(default='open')

    @classmethod
    def year2ref(cls, year):
        if dd.plugins.ledger.fix_y2k:
            if year < 2000:
                return str(year)[-2:]
            elif year < 3000:
                return chr(int(str(year)[-3:-1])+65) + str(year)[-1]
            else:
                raise Exception("20180827")
            # elif year < 2010:
            #     return "A" + str(year)[-1]
            # elif year < 2020:
            #     return "B" + str(year)[-1]
            # elif year < 2030:
            #     return "C" + str(year)[-1]
            # else:
                # raise Exception(20160304)
        # return str(year)[2:]
        return str(year)

    @classmethod
    def from_int(cls, year, *args):
        ref = cls.year2ref(year)
        return cls.get_by_ref(ref, *args)

    @classmethod
    def create_from_year(cls, year):
        ref = cls.year2ref(year)
        return cls(
            ref=ref, start_date=datetime.date(year, 1, 1),
            end_date=datetime.date(year, 12, 31))
        # obj.full_clean()
        # obj.save()
        # return obj

    @classmethod
    def get_or_create_from_date(cls, date):
        obj = cls.from_int(date.year, None)
        if obj is None:
            obj = cls.create_from_year(date.year)
            obj.full_clean()
            obj.save()
        return obj

    def __str__(self):
        return self.ref

class FiscalYears(dd.Table):
    model = 'ledger.FiscalYear'
    required_roles = dd.login_required(LedgerStaff)
    column_names = "ref start_date end_date state *"
    # detail_layout = """
    # ref id
    # start_date end_date
    # """


class PaymentTerm(BabelNamed, Referrable):

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Payment term")
        verbose_name_plural = _("Payment terms")

    ref_max_length = 5

    days = models.IntegerField(_("Days"), default=0)
    months = models.IntegerField(_("Months"), default=0)
    end_of_month = models.BooleanField(_("End of month"), default=False)

    printed_text = dd.BabelTextField(
        _("Printed text"), blank=True, format='plain')

    worker = dd.ForeignKey(
        dd.plugins.ledger.worker_model, null=True, blank=True,
        verbose_name=_("Worker"))


    def get_due_date(self, date1):
        assert isinstance(date1, datetime.date), \
            "%s is not a date" % date1
        d = date1 + relativedelta(months=self.months, days=self.days)
        if self.end_of_month:
            d = last_day_of_month(d)
        return d


class PaymentMethod(BabelDesignated):

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Payment method")
        verbose_name_plural = _("Payment methods")

    journal = dd.ForeignKey('ledger.Journal')


#
class Account(StructuredReferrable, BabelNamed, Sequenced):
    ref_max_length = settings.SITE.plugins.ledger.ref_length

    class Meta:
        verbose_name = _("Account")
        verbose_name_plural = _("Accounts")
        ordering = ['ref']
        app_label = 'ledger'

    sheet_item = dd.ForeignKey('sheets.Item', null=True, blank=True)
    common_account = CommonAccounts.field(blank=True)
    needs_partner = models.BooleanField(_("Needs partner"), default=False)
    clearable = models.BooleanField(_("Clearable"), default=False)
    # default_dc = DebitOrCreditField(_("Default booking direction"))
    vat_column = VatColumns.field(blank=True)
    vat_class = VatClasses.field(blank=True)
    default_amount = dd.PriceField(
        _("Default amount"), blank=True, null=True)

    @classmethod
    def get_simple_parameters(cls):
        yield "vat_class"
        yield "vat_column"
        yield "common_account"

    @dd.chooser()
    def sheet_item_choices(cls):
        return rt.models.sheets.Item.get_usable_items()

    def after_ui_save(self, ar, cw):
        super(Account, self).after_ui_save(ar, cw)
        if cw is None:
            return
        old = cw.get_old_value('common_account')
        new = self.common_account
        if old != new:
            if old is not None:
                old.set_object(None)
            if new is not None:
                new.set_object(self)

class Voucher(UserAuthored, Duplicable, UploadController, PeriodRangeObservable):
# class Voucher(UserAuthored, Duplicable, Registrable, UploadController, PeriodRangeObservable):

    class Meta:
        # abstract = True
        verbose_name = _("Voucher")
        verbose_name_plural = _("Vouchers")
        app_label = 'ledger'

    manager_roles_required = dd.login_required(VoucherSupervisor)
    # workflow_state_field = 'state'

    journal = JournalRef()
    entry_date = models.DateField(_("Entry date"))
    voucher_date = models.DateField(_("Voucher date"))
    accounting_period = dd.ForeignKey(
        'ledger.AccountingPeriod', blank=True)
    number = VoucherNumber(_("No."), blank=True, null=True)
    narration = models.CharField(_("Narration"), max_length=200, blank=True)

    # state = VoucherStates.field(default='draft')

    def unused_get_partner(self):
        # return None
        raise NotImplementedError(
            "{} must define get_partner()".format(self.__class__))

    def unused_get_wanted_movements(self):
        # deactivated this because MRO is complex, see 20200128
        # return []
        raise NotImplementedError(
            "{} must define get_wanted_movements()".format(self.__class__))

    @property
    def currency(self):
        """This is currently used only in some print templates.

        """
        return dd.plugins.ledger.currency_symbol

    @dd.displayfield(_("No."))
    def number_with_year(self, ar):
        return "{0}/{1}".format(self.number, self.accounting_period.year)

    @classmethod
    def quick_search_filter(model, search_text, prefix=''):
        """Overrides :meth:`lino.core.model.Model.quick_search_filter`.

        Examples:

        123 -> voucher number 123 in current year

        123/2014 -> voucher number 123 in 2014

        """
        # logger.info(
        #     "20160612 Voucher.quick_search_filter(%s, %r, %r)",
        #     model, search_text, prefix)
        parts = search_text.split('/')
        if len(parts) == 2:
            kw = {
                prefix + 'number': parts[0],
                prefix + 'accounting_period__year': parts[1]}
            return models.Q(**kw)
        if search_text.isdigit() and not search_text.startswith('0'):
            kw = {
                prefix + 'number': int(search_text),
                prefix + 'accounting_period__year':
                FiscalYear.get_or_create_from_date(dd.today())}
            return models.Q(**kw)
        return super(Voucher, model).quick_search_filter(search_text, prefix)

    def __str__(self):
        if self.number is None:
            return "{0}#{1}".format(self.journal.ref, self.id)
        # moved to implementing subclasses:
        #   if self.state not in dd.plugins.ledger.registered_states:
        #     # raise Exception("20191223 {} is not in {}".format(self.state, dd.plugins.ledger.registered_states))
        # assert self.number is not None
        if self.journal.yearly_numbering:
            return "{0} {1}/{2}".format(self.journal.ref, self.number,
                                        self.accounting_period.year)
        return "{0} {1}".format(self.journal.ref, self.number)
        # if self.journal.ref:
        #     return "%s %s" % (self.journal.ref,self.number)
        # return "#%s (%s %s)" % (self.number,self.journal,self.year)

    def full_clean(self, *args, **kwargs):
        if self.entry_date is None:
            self.entry_date = dd.today()
        if self.voucher_date is None:
            self.voucher_date = self.entry_date
        if not self.accounting_period_id:
            self.accounting_period = AccountingPeriod.get_default_for_date(
                self.entry_date)
        if self.number is None:
            self.number = self.journal.get_next_number(self)
        super(Voucher, self).full_clean(*args, **kwargs)

    def on_create(self, ar):
        super(Voucher, self).on_create(ar)
        if self.entry_date is None:
            if ar is None:
                self.entry_date = dd.today()
            else:
                info = LedgerInfo.get_for_user(ar.get_user())
                self.entry_date = info.entry_date or dd.today()

    def on_duplicate(self, ar, master):
        self.number = self.entry_date = self.accounting_period = None
        self.on_create(ar)
        super(Voucher, self).on_duplicate(ar, master)

    def entry_date_changed(self, ar):
        self.accounting_period = AccountingPeriod.get_default_for_date(
            self.entry_date)
        self.voucher_date = self.entry_date
        self.accounting_period_changed(ar)
        info = LedgerInfo.get_for_user(ar.get_user())
        info.entry_date = self.entry_date
        info.full_clean()
        info.save()

    def accounting_period_changed(self, ar):
        self.number = self.journal.get_next_number(self)

    def get_detail_action(self, ar):
        """Custom :meth:`get_detail_action
        <lino.core.model.Model.get_detail_action>` because the
        detail_layout to use depends on the journal's voucher type.

        """
        if self.journal_id:
            table = self.journal.voucher_type.table_class
            if table:
                ba = table.detail_action
                # 20201230 ba = ba.action.defining_actor.detail_action
                # if ar is None or ba.get_row_permission(ar, self, None):
                #     return ba
                if ar is None or ba.get_view_permission(
                        ar.get_user().user_type):
                    return ba
                return None
        return super(Voucher, self).get_detail_action(ar)

    def get_due_date(self):
        return self.entry_date

    def get_trade_type(self):
        return self.journal.trade_type

    def get_printed_name(self):
        return dd.babelattr(self.journal, 'printed_name')

    def get_movement_description(self, mvt, ar=None):
        if ar is None:
            return
        if self.narration:
            yield self.narration
        p = self.get_partner()
        if p is not None and p != ar.master_instance:
            yield ar.obj2html(p)
        if mvt.partner and mvt.partner != p:
            yield ar.obj2html(mvt.partner)

    def after_ui_save(self, ar, cw):
        super(Voucher, self).after_ui_save(ar, cw)
        tt = self.get_trade_type()
        if tt is None:
            return
        p = self.get_partner()
        if p is None:
            return
        account = tt.get_partner_invoice_account(p)
        if account is None:
            return
        if self.items.exists():
            return
        i = self.add_voucher_item(account=account)
        i.full_clean()
        i.save()

    @classmethod
    def get_journals(cls):
        vtypes = (vt for vt in VoucherTypes.get_list_items() if issubclass(cls, vt.model))
        # vt = VoucherTypes.get_for_model(cls)
        return Journal.objects.filter(voucher_type__in=vtypes).order_by('seqno')

    @dd.chooser()
    def unused_accounting_period_choices(cls, entry_date):
        # deactivated because it also limits the choices of the
        # parameter field (which is a Lino bug)
        return rt.models.ledger.AccountingPeriod.get_available_periods(
            entry_date)

    @dd.chooser()
    def journal_choices(cls):
        # logger.info("20140603 journal_choices %r", cls)
        return cls.get_journals()

    @classmethod
    def create_journal(cls, trade_type=None, account=None, **kw):
        vt = VoucherTypes.get_for_model(cls)
        if isinstance(trade_type, str):
            trade_type = TradeTypes.get_by_name(trade_type)
        if isinstance(account, str):
            account = rt.models.ledger.Account.get_by_ref(account)
        if account is not None:
            kw.update(account=account)
        return Journal(trade_type=trade_type, voucher_type=vt, **kw)

    # def get_default_match(self): removed 20191226
    #     return str(self)
        # return "%s#%s" % (self.journal.ref, self.id)
        # return "%s%s" % (self.id, self.journal.ref)

    # def get_voucher_match(self):
    #     return str(self)  # "{0}{1}".format(self.journal.ref, self.number)

    def do_and_clear(self, func, do_clear):
        existing_mvts = self.movement_set.all()
        partners = set()
        # accounts = set()
        if not self.journal.auto_check_clearings:
            do_clear = False
        if do_clear:
            for m in existing_mvts.filter(
                    account__clearable=True, partner__isnull=False):
                partners.add(m.partner)
        existing_mvts.delete()
        func(partners)
        if do_clear:
            for p in partners:
                check_clearings_by_partner(p)
            # for a in accounts:
            #     check_clearings_by_account(a)

        # dd.logger.info("20151211 Done cosi.Voucher.register_voucher()")

    def disable_delete(self, ar=None):
        msg = self.journal.disable_voucher_delete(self)
        if msg is not None:
            return msg
        return super(Voucher, self).disable_delete(ar)

    def create_movement(self, item, acc_tuple, project, amount, **kw):
        # dd.logger.info("20151211 ledger.create_movement()")
        # assert type(dc) != type(True)
        account, ana_account = acc_tuple
        if account is None and item is not None:
            raise Warning("No account specified for {}".format(item))
        if not isinstance(account, rt.models.ledger.Account):
            raise Warning("{} is not an Account object".format(account))
        kw['voucher'] = self
        kw['account'] = account
        if ana_account is not None:
            kw['ana_account'] = ana_account
        kw['value_date'] = self.entry_date
        if account.clearable:
            kw.update(cleared=False)
        else:
            kw.update(cleared=True)

        if dd.plugins.ledger.project_model:
            kw['project'] = project

        # if dc == DC.debit:  # 20201219  ledger.Account.create_movement
        #     amount = - amount
        kw['amount'] = amount

        b = rt.models.ledger.Movement(**kw)
        return b

    def get_mti_leaf(self):
        return mti.get_child(self, self.journal.voucher_type.model)

    # def obj2html(self, ar):
    def obj2href(self, ar):
        return ar.obj2html(self.get_mti_leaf())

    #~ def add_voucher_item(self,account=None,**kw):
        #~ if account is not None:
            #~ if not isinstance(account,ledger.Account):
            #~ if isinstance(account, str):
                #~ account = self.journal.chart.get_account_by_ref(account)
            #~ kw['account'] = account
    def add_voucher_item(self, account=None, **kw):
        if account is not None:
            if isinstance(account, str):
                account = rt.models.ledger.Account.get_by_ref(account)
            kw['account'] = account
        kw.update(voucher=self)
        #~ logger.info("20131116 %s",self.items.model)
        return self.items.model(**kw)
        #~ return super(AccountInvoice,self).add_voucher_item(**kw)

    def get_bank_account(self):
        """Return the `sepa.Account` object to which this voucher is to be
        paid. This is needed by
        :class:`lino_xl.lib.ledger.DueMovement`.

        """
        return None
        # raise NotImplementedError()

    def get_uploads_volume(self):
        if self.journal_id:
            return self.journal.uploads_volume


Voucher.set_widget_options('number_with_year', width=8)
# Voucher.set_widget_options('number', hide_sum=True)


class ToggleState(dd.Action):
    # show_in_bbar = False
    # button_text = _("Toggle state")
    # sort_index = 52
    label = _("Toggle state")
    # action_name = "changemystate"
    button_text = "⏼" # 23FC Toggle power

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        fld = ar.actor.workflow_state_field
        chl = fld.choicelist  # VoucherStates
        # print("20190722", obj)
        if obj.state == chl.draft:
            obj.set_workflow_state(ar, fld, chl.registered)
        elif obj.state == chl.registered:
            obj.set_workflow_state(ar, fld, chl.draft)
        else:
            raise Warning(_("Cannot toggle from state {}").format(obj.state))
        # obj.full_clean()
        # obj.save()
        ar.set_response(refresh=True)


class RegistrableVoucher(Registrable, Voucher):

    class Meta:
        abstract = True

    toggle_state = ToggleState()
    hide_editable_number = True

    def __str__(self):
        # if not isinstance(dd.plugins.ledger.registered_states, tuple):
        #     raise Exception("registered_states is {}".format(dd.plugins.ledger.registered_states))
        # if not isinstance(self.state, dd.plugins.ledger.registered_states):
        if self.hide_editable_number and self.state.is_editable:
            # raise Exception("20191223 {} is not in {}".format(self.state, dd.plugins.ledger.registered_states))
            return "{0} #{1}".format(self.journal.ref, self.id)
        return super(RegistrableVoucher, self).__str__()

    @classmethod
    def get_actions_hotkeys(cls):
        return [{'key': 'x',
                'ctrl': True,
                'shift': False,
                'ba': 'toggle_state'}]

    def after_state_change(self, ar, oldstate, newstate):
        # Movements are created *after* having changed the state because
        # otherwise the match isn't correct.
        if newstate.name == 'draft':
            self.deregister_voucher(ar)
        elif newstate.name == 'registered':
            self.register_voucher(ar)
        super(RegistrableVoucher, self).after_state_change(ar, oldstate, newstate)

    def register_voucher(self, ar=None, do_clear=True):
        """
        Delete any existing movements and re-create them.
        """
        # dd.logger.info("20151211 cosi.Voucher.register_voucher()")
        # self.year = FiscalYears.get_or_create_from_date(self.entry_date)
        # dd.logger.info("20151211 movement_set.all().delete()")

        # if self.number is None:
        #     self.number = self.journal.get_next_number(self)

        def doit(partners):
            seqno = 0
            # dd.logger.info("20151211 gonna call get_wanted_movements()")
            movements = self.get_wanted_movements()
            # dd.logger.info("20151211 gonna save %d movements", len(movements))
            # self.full_clean()
            # self.save()

            fcu = dd.plugins.ledger.suppress_movements_until
            for m in movements:
                # don't create movements before suppress_movements_until
                if fcu and m.value_date <= fcu:
                    continue
                # if we don't set seqno, Sequenced.full_clean will do
                # it, but at the price of an additional database
                # lookup.
                seqno += 1
                m.seqno = seqno
                # m.cleared = True
                try:
                    m.full_clean()
                except ValidationError as e:
                    dd.logger.warning("20181116 %s : %s", e, dd.obj2str(m))
                    return
                m.save()
                if m.partner:
                    partners.add(m.partner)
            if settings.SITE.history_aware_logging:
                dd.logger.info("Register %s (%d movements, %d partners)",
                    self, seqno, len(partners))

        self.do_and_clear(doit, do_clear)

    def deregister_voucher(self, ar, do_clear=True):

        def doit(partners):
            if settings.SITE.history_aware_logging:
                dd.logger.info("Deregister %s (%d partners)", self, len(partners))

        self.do_and_clear(doit, do_clear)


class Declaration(Payable, RegistrableVoucher, Certifiable, PeriodRange):
    class Meta:
        abstract = True
        app_label = "ledger"

    state = VoucherStates.field(default="draft")

    def get_match(self):
        # A declaration has no manual match field.
        return self

    def full_clean(self, *args, **kw):
        if self.entry_date:
            AP = rt.models.ledger.AccountingPeriod
            # declare the previous month by default
            if not self.start_period_id:
                self.start_period = AP.get_default_for_date(
                    self.entry_date)
                # self.start_period = AP.get_default_for_date(
                #     self.entry_date - AMONTH)

            # if not self.start_date:
            #     self.start_date = (self.voucher_date-AMONTH).replace(day=1)
            # if not self.end_date:
            #     self.end_date = self.start_date + AMONTH - ADAY
        # if self.voucher_date <= self.end_date:
        #    raise ValidationError(
        #        "Voucher date must be after the covered period")
        # self.compute_fields()
        super(Declaration, self).full_clean(*args, **kw)

class Movement(ProjectRelated, PeriodRangeObservable):
    allow_cascaded_delete = ['voucher']

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Movement")
        verbose_name_plural = _("Movements")

    observable_period_prefix = 'voucher__'

    # journal = JournalRef()
    # voucher_id = models.PositiveIntegerField(_("Voucher Id"))
    voucher = dd.ForeignKey('ledger.Voucher')
    partner = dd.ForeignKey(
        'contacts.Partner',
        related_name="%(app_label)s_%(class)s_set_by_partner",
        blank=True, null=True)
    seqno = models.IntegerField(_("Seq.No."))
    account = dd.ForeignKey('ledger.Account')
    amount = dd.PriceField(default=0, max_digits=14, decimal_places=2)
    # dc = DebitOrCreditField()
    match = models.CharField(_("Match"), blank=True, max_length=20)
    cleared = models.BooleanField(_("Cleared"), default=False)
    value_date = models.DateField(_("Value date"), null=True, blank=True)

    @dd.chooser(simple_values=True)
    def match_choices(cls, partner, account):
        qs = cls.objects.filter(
            partner=partner, account=account, cleared=False)
        qs = qs.order_by('value_date')
        return qs.values_list('match', flat=True)

    def select_text(self):
        v = self.voucher.get_mti_leaf()
        # v = self.voucher
        if v is None:
            return str(self.voucher)
        return "%s (%s)" % (v, v.entry_date)

    # @property
    # def voucher(self):
    #     return self.journal.voucher_type.model.objects.get(pk=self.voucher_id)
    #

    @dd.virtualfield(dd.PriceField(
        _("Debit")), sortable_by=['amount', 'value_date'])
    def debit(self, ar):
        return - self.amount if self.amount < 0 else None

    @dd.virtualfield(dd.PriceField(
        _("Credit")), sortable_by=['-amount', 'value_date'])
    def credit(self, ar):
        return self.amount if self.amount > 0 else None

    @dd.displayfield(
        _("Voucher"), sortable_by=[
            'voucher__journal__ref', 'voucher__accounting_period__year',
            'voucher__number'])
    def voucher_link(self, ar):
        if ar is None:
            return ''
        return ar.obj2html(self.voucher.get_mti_leaf())
        # return ar.obj2html(self.voucher)

    @dd.displayfield(_("Voucher partner"))
    def voucher_partner(self, ar):
        if ar is None:
            return ''
        voucher = self.voucher.get_mti_leaf()
        # voucher = self.voucher
        if voucher is None:
            return ''
        p = voucher.get_partner()
        if p is None:
            return ''
        return ar.obj2html(p)

    @dd.displayfield(_("Match"), sortable_by=['match'])
    def match_link(self, ar):
        if ar is None or not self.match:
            return ''
        sar = rt.models.ledger.MovementsByMatch.request(
            master_instance=self.match, parent=ar)
        return sar.ar2button(label=self.match)

    #~ @dd.displayfield(_("Matched by"))
    #~ def matched_by(self,ar):
        #~ elems = [obj.voucher_link(ar) for obj in Movement.objects.filter(match=self)]
        #~ return E.div(*elems)

    def get_siblings(self):
        return self.voucher.movement_set.all()
        #~ return self.__class__.objects.filter().order_by('seqno')

    def __str__(self):
        return "%s.%d" % (str(self.voucher), self.seqno)

    # def get_match(self):
    #     return self.match or str(self.voucher)

    @classmethod
    def get_balance(cls, dc, qs):
        bal = ZERO
        for mvt in qs:
            bal += mvt.amount
        return dc.normalized_amount(bal)

    @classmethod
    def balance_info(cls, dc, **kwargs):
        qs = cls.objects.filter(**kwargs)
        qs = qs.order_by('value_date')
        bal = ZERO
        s = ''
        for mvt in qs:
            bal += mvt.amount
            if mvt.amount > 0:
                s += ' +' + str(dc.normalized_amount(mvt.amount))
            else:
                s += str(mvt.amount)
            s += " ({0}) ".format(mvt.voucher)
            # s += " ({0} {1}) ".format(
            #     mvt.voucher,
            #     dd.fds(mvt.voucher.voucher_date))
        if bal:
            return s + "= " + str(dc.normalized_amount(bal))
        return ''
        if False:
            from lino_xl.lib.cal.utils import day_and_month
            mvts = []
            for dm in get_due_movements(DC.credit, models.Q(partner=self.pupil)):
                s = dm.match
                s += " [{0}]".format(day_and_month(dm.due_date))
                s += " ("
                s += ', '.join([str(i.voucher) for i in dm.debts])
                if len(dm.payments):
                    s += " - "
                    s += ', '.join([str(i.voucher) for i in dm.payments])
                s += "): {0}".format(dm.balance)
                mvts.append(s)
            return '\n'.join(mvts)


Movement.set_widget_options('voucher_link', width=12)


class MatchRule(dd.Model):

    class Meta:
        app_label = 'ledger'
        verbose_name = _("Match rule")
        verbose_name_plural = _("Match rules")
        unique_together = ['account', 'journal']

    account = dd.ForeignKey('ledger.Account')
    journal = JournalRef()

    allow_cascaded_delete = "journal"

    @dd.chooser()
    def unused_account_choices(self, journal):
        # would be nice, but doesn't work because matchrules are
        # usually entered via MatchRulesByJournal where journal is
        # always None.
        if journal:
            fkw = {journal.trade_type.name + '_allowed': True}
            return rt.models.ledger.Account.objects.filter(**fkw)
        print("20151221 journal is None")
        return []


for tt in TradeTypes.objects():
    dd.inject_field(
        'ledger.Account',
        tt.name + '_allowed',
        models.BooleanField(
            verbose_name=tt.text, default=False,
            help_text=format_lazy(
                _("Whether this account is available for {} transactions."), tt.text)))


dd.inject_field(
    'contacts.Partner',
    'payment_term',
    dd.ForeignKey(
        'ledger.PaymentTerm',
        blank=True, null=True,
        help_text=_("The default payment term for "
                    "sales invoices to this customer.")))


class VoucherChecker(Checker):
    verbose_name = _("Check integrity of ledger vouchers")
    messages = dict(
        missing=_("Missing movement {0}."),
        unexpected=_("Unexpected movement {0}."),
        diff=_("Movement {0} : {1}"),
        warning=_("Failed to get movements for {0} : {1}"),
    )

    def get_checkable_models(self):
        return rt.models_by_base(Voucher)  # also MTI children

    def get_checkdata_problems(self, obj, fix=False):
        if obj.__class__ is rt.models.ledger.Voucher:
            if obj.get_mti_leaf() is None:
                yield (True, _("Voucher without MTI leaf"))
                if fix:
                    obj.movement_set.all().delete()
                    obj.delete()
            return

        def m2k(obj):
            return obj.seqno

        wanted = dict()
        # if obj.state in dd.plugins.ledger.registered_states:
        if not obj.state.is_editable:
            seqno = 0
            fcu = dd.plugins.ledger.suppress_movements_until
            try:
                for m in obj.get_wanted_movements():
                    if fcu and m.value_date <= fcu:
                        continue
                    seqno += 1
                    m.seqno = seqno
                    # if fcu and m.value_date <= fcu:
                    #     m.cleared = True
                    m.full_clean()
                    wanted[m2k(m)] = m
            except Warning as e:
                yield (False, self.messages['warning'].format(obj, e))
                return

        for em in obj.movement_set.order_by('seqno'):
            wm = wanted.pop(m2k(em), None)
            if wm is None:
                yield (False, self.messages['unexpected'].format(em))
                return
            diffs = []
            for k in ('partner_id', 'account_id', 'amount', 'value_date'):
                emv = getattr(em, k)
                wmv = getattr(wm, k)
                if emv != wmv:
                    diffs.append(u"{} ({}!={})".format(k, emv, wmv))
            if len(diffs) > 0:
                yield (False, self.messages['diff'].format(
                    em, u', '.join(diffs)))
                return

        if wanted:
            for missing in wanted.values():
                yield (False, self.messages['missing'].format(missing))
                return


VoucherChecker.activate()


class PartnerHasOpenMovements(ObservedEvent):
    text = _("Has open movements")

    def add_filter(self, qs, pv):
        qs = qs.filter(ledger_movement_set_by_partner__cleared=False)
        if pv.end_date:
            qs = qs.filter(ledger_movement_set_by_partner__value_date__lte=pv.end_date)
        if pv.start_date:
            qs = qs.filter(ledger_movement_set_by_partner__value_date__gte=pv.start_date)
        return qs.distinct()

PartnerEvents.add_item_instance(
    PartnerHasOpenMovements("has_open_movements"))

on_ledger_movement = Signal(['instance'])


class DueMovement(TableRow):
    def __init__(self, dc, mvt):
        self.dc = dc
        # self.match = mvt.get_match()
        self.match = mvt.match
        self.partner = mvt.partner
        self.account = mvt.account
        self.project = mvt.project
        self.pk = self.id = mvt.id
        self.obj2href = mvt.obj2href
        self.trade_type = None
        # for tt in TradeTypes.get_list_items():
        #     if tt.get_main_account() == self.account:
        #         self.trade_type = tt
        #         break
        self.debts = []
        self.payments = []
        self.balance = ZERO
        self.due_date = None
        self.has_unsatisfied_movement = False
        self.has_satisfied_movement = False
        self.bank_account = None

        # self.collect(mvt)

        # flt = dict(partner=self.partner, account=self.account,
        #            match=self.match)
        # if self.project:
        #     flt.update(project=self.project)
        # else:
        #     flt.update(project__isnull=True)
        # qs = rt.models.ledger.Movement.objects.filter(**flt)
        # for mvt in qs.order_by('voucher__date'):
        #     self.collect(mvt)

    def __repr__(self):
        return "{0} {1} {2}".format(
            dd.obj2str(self.partner), self.match, self.balance)

    def collect_all(self):
        flt = dict(
            partner=self.partner, account=self.account, match=self.match)
        for mvt in rt.models.ledger.Movement.objects.filter(**flt):
            self.collect(mvt)

    def collect(self, mvt):
        """
        Add the given movement to the list of movements that are being
        cleared by this DueMovement.

        "debts" here means "movements in the expected direction", "payments"
        are movements that decrease the balance, i.e. go in the opposite of
        the expected direction.


        """
        # dd.logger.info("20160604 collect %s", mvt)
        if mvt.cleared:
            self.has_satisfied_movement = True
        else:
            self.has_unsatisfied_movement = True

        voucher = mvt.voucher.get_mti_leaf()
        # voucher = mvt.voucher
        if voucher is None:
            return
        due_date = voucher.get_due_date()
        if self.due_date is None or due_date < self.due_date:
            self.due_date = due_date

        if self.trade_type is None:
            self.trade_type = voucher.get_trade_type()
            # print("20201014 found trade type", self.trade_type, "from", mvt)
        amount = self.dc.normalized_amount(mvt.amount)  # 20201219  DueMovement.collect()
        # if self.dc == DC.debit:
        #     amount = - amount
        # self.balance += myround(mvt.amount)
        self.balance += amount

        if amount < 0:  # 20201219  DueMovement.collect()
            self.debts.append(mvt)
            bank_account = voucher.get_bank_account()
            if bank_account is not None:
                if self.bank_account != bank_account:
                    self.bank_account = bank_account
                elif self.bank_account != bank_account:
                    raise Exception("More than one bank account")
            # else:
            #     dd.logger.info(
            #         "20150810 no bank account for {0}".format(voucher))

        else:
            self.payments.append(mvt)

    def unused_check_clearings(self):
        """Check whether involved movements are cleared or not, and update
        their :attr:`cleared` field accordingly.

        """
        cleared = self.balance == ZERO
        if cleared:
            if not self.has_unsatisfied_movement:
                return
        else:
            if not self.has_satisfied_movement:
                return
        for m in self.debts + self.payments:
            if m.cleared != cleared:
                m.cleared = cleared
                m.save()


def get_due_movements(dc, flt):
    if dc is None:
        return
    qs = rt.models.ledger.Movement.objects.filter(flt)
    qs = qs.filter(account__clearable=True)
    # qs = qs.exclude(match='')
    qs = qs.order_by(*dd.plugins.ledger.remove_dummy(
        'value_date', 'account__ref', 'partner', 'project', 'id'))
    matches_by_account = dict()
    matches = []
    for mvt in qs:
        k = (mvt.account, mvt.partner, mvt.project, mvt.match)
        # k = (mvt.account, mvt.partner, mvt.project, mvt.get_match())
        dm = matches_by_account.get(k)
        if dm is None:
            dm = DueMovement(dc, mvt)
            matches_by_account[k] = dm
            matches.append(dm)
        dm.collect(mvt)
    for m in matches:
        if m.balance:
            yield m


def check_clearings_by_account(account, matches=[]):
    # not used. See blog/2017/0802.rst
    qs = rt.models.ledger.Movement.objects.filter(
        account=account).order_by('match')
    check_clearings(qs, matches)
    on_ledger_movement.send(sender=account.__class__, instance=account)

def check_clearings_by_partner(partner, matches=[]):
    qs = rt.models.ledger.Movement.objects.filter(
        partner=partner).order_by('match')
    check_clearings(qs, matches)
    on_ledger_movement.send(sender=partner.__class__, instance=partner)

def check_clearings(qs, matches=[]):
    qs = qs.select_related('voucher', 'voucher__journal')
    if len(matches):
        qs = qs.filter(match__in=matches)
    # fcu = dd.plugins.ledger.suppress_movements_until
    # if fcu:
    #     qs = qs.exclude(value_date__lte=fcu)
    sums = SumCollector()
    for mvt in qs:
        k = (mvt.match, mvt.account)
        sums.collect(k, mvt.amount)

    for k, balance in sums.items():
        match, account = k
        sat = (balance == ZERO)
        # if not sat:
        #     print("20201014 {} != {}".format(balance, ZERO))
        qs.filter(account=account, match=match).update(cleared=sat)
