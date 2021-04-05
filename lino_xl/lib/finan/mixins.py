# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

# from lino.mixins.registrable import Registrable
from lino.modlib.checkdata.choicelists import Checker
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.ledger.utils import DC, ZERO, MAX_AMOUNT, myround
from lino_xl.lib.ledger.mixins import VoucherItem, SequencedVoucherItem
from lino_xl.lib.ledger.mixins import ProjectRelated, Matching
from etgen.html import E

from lino.api import dd, rt, _

from lino_xl.lib.ledger.choicelists import VoucherStates

ledger = dd.resolve_app('ledger')


class FinancialVoucher(ledger.RegistrableVoucher, Certifiable):

    auto_compute_amount = False

    class Meta:
        abstract = True
        app_label = "finan"

    state = ledger.VoucherStates.field(default='draft')
    item_account = dd.ForeignKey(
        'ledger.Account',
        verbose_name=_("Default account"),
        blank=True, null=True)
    item_remark = models.CharField(
        _("Your reference"), max_length=200, blank=True)

    # def after_state_change(self, ar, old, new):
    #     super(FinancialVoucher, self).after_state_change(ar, old, new)
    #     if self.journal.auto_check_clearings:
    #         self.check_clearings()

    def due2itemdict(self, due, **kwargs):
        if not due.balance:
            raise Exception("20201010")
        # print("20201014", due.account, due.trade_type)
        kwargs.update(match=due.match, account=due.account)
        if due.trade_type and not due.account:  # 20201014
            ma = due.trade_type.get_main_account()
            if ma:
                kwargs.update(account=ma)
        if due.project:
            kwargs.update(project=due.project)
        if due.partner:
            kwargs.update(partner=due.partner)
        # kwargs.update(amount=due.balance)  # 20201219 FinancialVoucher.due2itemdict
        if due.dc == self.journal.dc:
            kwargs.update(amount=-due.balance)  # 20201219 FinancialVoucher.due2itemdict
        else:
            kwargs.update(amount=due.balance)  # 20201219 FinancialVoucher.due2itemdict
        return kwargs

    def add_item_from_due(self, obj, **kwargs):
        kwargs = self.due2itemdict(obj, **kwargs)
        i = self.add_voucher_item(**kwargs)
        return i

    def get_partner(self):
        return None

    # def get_wanted_movements(self):
    #     raise NotImplemented()

    def get_finan_movements(self):
        """Yield the movements to be booked for this finanical voucher.

        This method is expected to return a tuple ``(amount,
        movements_and_items)``, where `amount` is the total amount and
        `movements_and_items` is a sequence of tuples ``(mvt, item)``
        where `mvt` is a :class:`Movement` object to be saved and
        `item` is the (existing) voucher item that caused this movement.

        """
        # dd.logger.info("20151211 get_finan_movements()")
        amount = ZERO
        movements_and_items = []
        for i in self.items.order_by('seqno'):
            # kw = dict(seqno=i.seqno, partner=i.partner)
            kw = dict(partner=i.get_partner())
            kw.update(match=i.get_match())
            if abs(i.amount > MAX_AMOUNT):
                raise Exception("Oops, {} is too big ({}, {})".format(i.amount, self, kw))
                # dd.logger.warning("Oops, %s is too big", i.amount)
                # return (ZERO, [])
            b = self.create_movement(
                i, (i.account or self.item_account, None),
                i.project, i.amount, **kw)
            amount += i.amount
            movements_and_items.append((b, i))
        return amount, movements_and_items


class FinancialVoucherItem(VoucherItem, SequencedVoucherItem,
                           ProjectRelated, Matching):
    class Meta:
        abstract = True
        verbose_name = _("Item")
        verbose_name_plural = _("Items")
        app_label = "finan"

    amount = dd.PriceField(_("Amount"), default=ZERO, null=False)
    # dc = DebitOrCreditField()
    remark = models.CharField(
        _("Your reference"), max_length=200, blank=True)
    account = dd.ForeignKey('ledger.Account', blank=True, null=True)
    partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)

    quick_search_fields = 'remark account__ref account__name partner__name'

    @dd.chooser(simple_values=True)
    def match_choices(cls, voucher, partner):
        fkw = {}
        if not dd.plugins.finan.suggest_future_vouchers:
            fkw.update(value_date__lte=voucher.entry_date)
        return cls.get_match_choices(voucher.journal, partner, **fkw)

    def add_item_from_due(self, obj, **kwargs):
        return self.voucher.add_item_from_due(obj, **kwargs)

    # def get_default_match(self): # 20191226
    def __str__(self):
        """Used as `match` when no explicit match is specified for
        this movement.

        """
        if self.voucher_id and self.voucher.journal_id:
            return "%s %s:%s" % (
                self.voucher.journal.ref, self.voucher.number, self.seqno)
            # return str(self.date)
        return models.Model.__str__(self)
        # return super(FinancialVoucherItem, self).__str__()

    def get_siblings(self):
        return self.voucher.items.all()

    def collect_suggestions(self, ar, flt):
        suggestions = list(ledger.get_due_movements(
            self.voucher.journal.dc, flt))
        # dd.logger.info("20210106 %s", suggestions)
        if len(suggestions) == 0:
            self.match = ""
        elif len(suggestions) == 1:
            self.fill_suggestion(suggestions[0])
        elif ar:
            self.match = _("{} suggestions").format(len(suggestions))

            # def ok(ar2):
            #     # self.fill_suggestion(suggestions[0])
            #     # self.set_grouper(suggestions)
            #     ar2.error(_("Oops, not implemented."))
            #     return

            # elems = ["Cool! ", E.b(str(self.partner)),
            #          " has ", E.b(str(len(suggestions))),
            #          " suggestions! Click "]
            # ba = ar.actor.get_action_by_name('suggest')
            # elems.append(ar.action_button(ba, self))
            # elems.append(".")
            # html = E.p(*elems)
            # # dd.logger.info("20160526 %s", E.tostring(html))
            # ar.success(E.tostring(html), alert=True)
            # # ar.confirm(ok, E.tostring(html))

    def match_changed(self, ar):
        if not self.match or not self.voucher.journal.auto_fill_suggestions:
            return
        flt = dict(match=self.match, cleared=False)
        if not dd.plugins.finan.suggest_future_vouchers:
            flt.update(value_date__lte=self.voucher.entry_date)
        self.collect_suggestions(ar, models.Q(**flt))
        self.guess_amount()

    def partner_changed(self, ar):
        # dd.logger.info("20210106 FinancialMixin.partner_changed %s", self.amount)
        if self.amount:
            return
        if not self.partner or not self.voucher.journal.auto_fill_suggestions:
            return
        flt = dict(partner=self.partner, cleared=False)
        if not dd.plugins.finan.suggest_future_vouchers:
            flt.update(value_date__lte=self.voucher.entry_date)
        if self.match:
            flt.update(match=self.match)
        self.collect_suggestions(ar, models.Q(**flt))
        self.guess_amount()

    def debit_changed(self, ar):
        self.guess_amount()
    def credit_changed(self, ar):
        self.guess_amount()
    def amount_changed(self, ar):
        self.guess_amount()

    def account_changed(self, ar):
        if self.amount:
            return
        if not self.account:
            return
        if self.account.default_amount:
            self.amount = self.voucher.journal.dc.normalized_amount(self.account.default_amount)
            return
        if self.account.clearable and self.voucher.journal.auto_fill_suggestions:
            flt = dict(account=self.account, partner=self.partner, cleared=False)
            if not dd.plugins.finan.suggest_future_vouchers:
                flt.update(value_date__lte=self.voucher.entry_date)
            if self.match:
                flt.update(match=self.match)
            self.collect_suggestions(ar, models.Q(**flt))
        self.guess_amount()

    def get_partner(self):
        return self.partner or self.project

    def fill_suggestion(self, due):
        """Fill the fields of this item from the given suggestion (a
        `DueMovement` instance).

        """
        for k, v in self.voucher.due2itemdict(due).items():
            setattr(self, k, v)

    def guess_amount(self):
        if self.amount:
            return
        self.amount = ZERO
        if self.voucher.auto_compute_amount:
            q = self.voucher.items.exclude(id=self.id).annotate(models.Sum('amount'))
            # print("20210108", q[0].amount__sum)
            self.amount = -myround(q[0].amount__sum)

    def full_clean(self, *args, **kwargs):
        if self.amount is None:
            self.amount = ZERO  # just in case...

        if True: # temporarily deactivated for data migration
            problems = list(FinancialVoucherItemChecker.check_instance(self))
            if len(problems):
                raise ValidationError("20181120 {}".format(
                    '\n'.join([str(p[1]) for p in problems])))

        # dd.logger.info("20151117 FinancialVoucherItem.full_clean a %s", self.amount)
        super(FinancialVoucherItem, self).full_clean(*args, **kwargs)
        # dd.logger.info("20151117 FinancialVoucherItem.full_clean b %s", self.amount)


class FinancialVoucherItemChecker(Checker):

    model = FinancialVoucherItem
    verbose_name = _("Check for invalid account/partner combination")

    def get_checkdata_problems(self, obj, fix=False):
        # if obj.account_id and not obj.voucher.journal.auto_fill_suggestions:
        # if obj.account_id and not obj.voucher.auto_compute_amount:
        if obj.account_id and not obj.voucher.journal.preliminary:
            if obj.account.needs_partner:
                if not obj.partner_id:
                    yield (False, _("Account {} needs a partner").format(obj.account))
            else:
                if obj.partner_id:
                    yield (False,
                           _("Account {} cannot be used with a partner").format(obj.account))


FinancialVoucherItemChecker.activate()





class DatedFinancialVoucher(FinancialVoucher):
    class Meta:
        app_label = 'finan'
        abstract = True
    last_item_date = models.DateField(blank=True, null=True)

    def create_movement(self, item, *args, **kwargs):
        mvt = super(DatedFinancialVoucher, self).create_movement(
            item, *args, **kwargs)
        if item is not None and item.date:
            mvt.value_date = item.date
        return mvt


class DatedFinancialVoucherItem(FinancialVoucherItem):

    class Meta:
        app_label = 'finan'
        abstract = True

    date = models.DateField(_("Date"), blank=True, null=True)

    def on_create(self, ar):
        super(DatedFinancialVoucherItem, self).on_create(ar)
        if self.voucher.last_item_date:
            self.date = self.voucher.last_item_date
        # else:
        #     self.date = dd.today()

    def date_changed(self, ar):
        obj = self.voucher
        if obj.last_item_date != self.date:
            obj.last_item_date = self.date
            obj.full_clean()
            obj.save()

    def fill_suggestion(self, due):
        super(DatedFinancialVoucherItem, self).fill_suggestion(due)
        if self.voucher.last_item_date:
            self.date = self.voucher.last_item_date
