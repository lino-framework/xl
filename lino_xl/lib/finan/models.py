# Copyright 2008-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
# from django.core.exceptions import ValidationError

from etgen.html import E, join_elems

from lino_xl.lib.ledger.utils import ZERO, MAX_AMOUNT
from lino_xl.lib.ledger.fields import DcAmountField
from lino_xl.lib.ledger.choicelists import DC, VoucherTypes
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
from lino_xl.lib.ledger.mixins import ProjectRelated
from lino_xl.lib.ledger.mixins import PartnerRelated
from lino_xl.lib.sepa.mixins import BankAccount
from lino.modlib.printing.mixins import Printable

from lino.api import dd, rt, _

from .mixins import (FinancialVoucher, FinancialVoucherItem,
                     DatedFinancialVoucher, DatedFinancialVoucherItem)

from .actions import WritePaymentsInitiation


ledger = dd.resolve_app('ledger')


def warn_jnl_account(jnl):
    fld = jnl._meta.get_field('account')
    raise Warning(_("Field '{0}' in journal '{0}' is empty!").format(
        fld.verbose_name, jnl))


class ShowSuggestions(dd.Action):
    # started as a copy of ShowSlaveTable
    # TABLE2ACTION_ATTRS = tuple('help_text icon_name label sort_index'.split())
    TABLE2ACTION_ATTRS = tuple('help_text label sort_index'.split())
    show_in_bbar = False
    show_in_workflow = True
    readonly = False

    @classmethod
    def get_actor_label(self):
        return self._label or self.slave_table.label

    def attach_to_actor(self, actor, name):
        if actor.suggestions_table is None:
            # logger.info("%s has no suggestions_table", actor)
            return  # don't attach
        if isinstance(actor.suggestions_table, str):
            T = rt.models.resolve(actor.suggestions_table)
            if T is None:
                raise Exception("No table named %s" % actor.suggestions_table)
            actor.suggestions_table = T
        for k in self.TABLE2ACTION_ATTRS:
            setattr(self, k, getattr(actor.suggestions_table, k))
        return super(ShowSuggestions, self).attach_to_actor(actor, name)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        sar = ar.spawn(ar.actor.suggestions_table, master_instance=obj)
        js = ar.renderer.request_handler(sar)
        ar.set_response(eval_js=js)

    def unused_get_action_permission(self, ar, obj, state):
        # It would more intuitive to show Suggestions only for lines
        # with a partner.  But there are cases where we use it on an
        # empty item in order to select suggestions from multiple
        # partners.
        if not obj.get_partner():
            return False
        return super(ShowSuggestions, self).get_action_permission(
            ar, obj, state)


class JournalEntry(DatedFinancialVoucher, ProjectRelated):
    auto_compute_amount = True
    class Meta:
        app_label = 'finan'
        abstract = dd.is_abstract_model(__name__, 'JournalEntry')
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")

    # show_items = dd.ShowSlaveTable('finan.ItemsByJournalEntry')

    def get_wanted_movements(self):
        # dd.logger.info("20151211 FinancialVoucher.get_wanted_movements()")
        amount, movements_and_items = self.get_finan_movements()
        if amount:
            raise Warning(_("Missing amount {} in movements").format(
                amount))
        for m, i in movements_and_items:
            yield m

class PaymentOrder(FinancialVoucher, Printable):
    class Meta:
        app_label = 'finan'
        abstract = dd.is_abstract_model(__name__, 'PaymentOrder')
        verbose_name = _("Payment Order")
        verbose_name_plural = _("Payment Orders")

    total = dd.PriceField(_("Total"), blank=True, null=True)
    execution_date = models.DateField(
        _("Execution date"), blank=True, null=True)

    # show_items = dd.ShowSlaveTable('finan.ItemsByPaymentOrder')
    write_xml = WritePaymentsInitiation()

    @dd.displayfield(_("Print"))
    def print_actions(self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.instance_action_button(
            self.write_xml))
        return E.p(*join_elems(elems, sep=", "))

    def get_wanted_movements(self):
        """Implements
        :meth:`lino_xl.lib.ledger.Voucher.get_wanted_movements`
        for payment orders.

        As a side effect this also computes the :attr:`total` field and saves
        the voucher.

        """
        # dd.logger.info("20151211 cosi.PaymentOrder.get_wanted_movements()")
        acc = self.journal.account
        if not acc:
            warn_jnl_account(self.journal)
        # TODO: what if the needs_partner of the journal's account
        # is not checked? Shouldn't we raise an error here?
        amount, movements_and_items = self.get_finan_movements()
        if abs(amount) > MAX_AMOUNT:
            # dd.logger.warning("Oops, {} is too big ({})".format(amount, self))
            raise Exception("Oops, {} is too big ({})".format(amount, self))
            return
        self.total = self.journal.dc.normalized_amount(-amount)  # PaymentOrder.get_wanted_movements()
        # if self.journal.dc == DC.debit:  # PaymentOrder.get_wanted_movements()
        #     self.total = -amount
        # else:
        #     self.total = amount
        item_partner = self.journal.partner is None
        for m, i in movements_and_items:
            yield m
            if item_partner:
                yield self.create_movement(
                    i, (acc, None), m.project, -m.amount,  # 20201219 PaymentOrder.get_wanted_movements
                    partner=m.partner, match=i.get_match())
        if not item_partner:
            yield self.create_movement(
                None, (acc, None), None, -amount,  # 20201219 PaymentOrder.get_wanted_movements
                partner=self.journal.partner, match=self)
                # 20191226 partner=self.journal.partner, match=self.get_default_match())
        # no need to save() because this is called during set_workflow_state()
        # self.full_clean()
        # self.save()

    def add_item_from_due(self, obj, **kwargs):
        # if obj.bank_account is None:
        #     return
        i = super(PaymentOrder, self).add_item_from_due(obj, **kwargs)
        i.bank_account = obj.bank_account
        return i

    # def full_clean(self, *args, **kwargs):
    #     super(PaymentOrder, self).full_clean(*args, **kwargs)


class BankStatement(DatedFinancialVoucher):
    class Meta:
        app_label = 'finan'
        abstract = dd.is_abstract_model(__name__, 'BankStatement')
        verbose_name = _("Bank Statement")
        verbose_name_plural = _("Bank Statements")

    balance1 = dd.PriceField(_("Old balance"), default=ZERO)
    balance2 = dd.PriceField(_("New balance"), default=ZERO, blank=True)

    # show_items = dd.ShowSlaveTable('finan.ItemsByBankStatement')

    def get_previous_voucher(self):
        if not self.journal_id:
            #~ logger.info("20131005 no journal")
            return None
        qs = self.__class__.objects.filter(
            journal=self.journal).order_by('-entry_date')
        if qs.count() > 0:
            #~ logger.info("20131005 no other vouchers")
            return qs[0]

    def on_create(self, ar):
        super(BankStatement, self).on_create(ar)
        if self.balance1 == ZERO:
            prev = self.get_previous_voucher()
            if prev is not None:
                #~ logger.info("20131005 prev is %s",prev)
                self.balance1 = prev.balance2

    def on_duplicate(self, ar, master):
        self.balance1 = self.balance2 = ZERO
        super(BankStatement, self).on_duplicate(ar, master)

    def get_wanted_movements(self):
        """Implements
        :meth:`lino_xl.lib.ledger.Voucher.get_wanted_movements`
        for bank statements.

        As a side effect this also computes the :attr:`balance1` and
        :attr:`balance2` fields and saves the voucher.

        """
        # dd.logger.info("20151211 cosi.BankStatement.get_wanted_movements()")
        a = self.journal.account
        if not a:
            warn_jnl_account(self.journal)
        amount, movements_and_items = self.get_finan_movements()
        # dd.logger.info("20210106 %s %s %s", self.balance2, self.balance1, amount)
        self.balance2 = self.balance1 + self.journal.dc.normalized_amount(amount)  # 20201219 BankStatement.get_wanted_movements()
        # if self.journal.dc == DC.credit:  # 20201219 BankStatement.get_wanted_movements()
        #     self.balance2 = self.balance1 + amount
        # else:
        #     self.balance2 = self.balance1 - amount
        if abs(self.balance2) > MAX_AMOUNT:
            # dd.logger.warning("Oops, %s is too big", self.balance2)
            raise Exception("Oops, {} is too big ({})".format(self.balance2, self))
            return
        for m, i in movements_and_items:
            yield m
        yield self.create_movement(None, (a, None), None, amount)
        # no need to save() because this is called during set_workflow_state()
        # self.full_clean()
        # self.save()


class JournalEntryItem(DatedFinancialVoucherItem):
    class Meta:
        app_label = 'finan'
        verbose_name = _("Journal Entry item")
        verbose_name_plural = _("Journal Entry items")
    voucher = dd.ForeignKey('finan.JournalEntry', related_name='items')
    debit = DcAmountField(DC.debit, _("Debit"))
    credit = DcAmountField(DC.credit, _("Credit"))


class BankStatementItem(DatedFinancialVoucherItem):
    class Meta:
        app_label = 'finan'
        verbose_name = _("Bank Statement item")
        verbose_name_plural = _("Bank Statement items")
    voucher = dd.ForeignKey('finan.BankStatement', related_name='items')
    expense = DcAmountField(DC.debit, _("Expense"))
    income = DcAmountField(DC.credit, _("Income"))


class PaymentOrderItem(BankAccount, FinancialVoucherItem):
    class Meta:
        app_label = 'finan'
        verbose_name = _("Payment Order item")
        verbose_name_plural = _("Payment Order items")

    voucher = dd.ForeignKey('finan.PaymentOrder', related_name='items')
    # bank_account = dd.ForeignKey('sepa.Account', blank=True, null=True)
    to_pay = DcAmountField(DC.debit, _("To pay"))  # 20201219 PaymentOrderItem

    # def partner_changed(self, ar):
    #     FinancialVoucherItem.partner_changed(self, ar)
    #     BankAccount.partner_changed(self, ar)

    # def full_clean(self, *args, **kwargs):

    #     super(PaymentOrderItem, self).full_clean(*args, **kwargs)

# dd.update_field(PaymentOrderItem, 'iban', blank=True)
# dd.update_field(PaymentOrderItem, 'bic', blank=True)


class JournalEntryDetail(dd.DetailLayout):
    main = "general more"

    general = dd.Panel("""
    entry_date number:6 workflow_buttons
    narration
    finan.ItemsByJournalEntry
    """, label=_("General"))

    more = dd.Panel("""
    journal accounting_period user id
    item_account item_remark
    ledger.MovementsByVoucher
    """, label=_("More"))


class PaymentOrderDetail(JournalEntryDetail):
    general = dd.Panel("""
    entry_date number:6 total execution_date workflow_buttons
    narration
    finan.ItemsByPaymentOrder
    """, label=_("General"))


class BankStatementDetail(JournalEntryDetail):
    general = dd.Panel("""
    general_left uploads.UploadsByController
    finan.ItemsByBankStatement
    """, label=_("General"))

    general_left = """
    entry_date number:6 balance1 balance2
    narration workflow_buttons
    """


class FinancialVouchers(dd.Table):
    model = 'finan.JournalEntry'
    required_roles = dd.login_required(LedgerUser)
    params_panel_hidden = True
    order_by = ["id", "entry_date"]
    parameters = dict(
        pyear=dd.ForeignKey('ledger.FiscalYear', blank=True),
        #~ ppartner=dd.ForeignKey('contacts.Partner',blank=True,null=True),
        pjournal=ledger.JournalRef(blank=True))
    params_layout = "pjournal pyear"
    detail_layout = JournalEntryDetail()
    insert_layout = dd.InsertLayout("""
    entry_date
    narration
    """, window_size=(40, 'auto'))

    suggest = ShowSuggestions()
    suggestions_table = None  # 'finan.SuggestionsByJournalEntry'

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        qs = super(FinancialVouchers, cls).get_request_queryset(ar, **kwargs)
        if not isinstance(qs, list):
            if ar.param_values.pyear:
                qs = qs.filter(accounting_period__year=ar.param_values.pyear)
            if ar.param_values.pjournal:
                qs = qs.filter(journal=ar.param_values.pjournal)
        return qs


class JournalEntries(FinancialVouchers):
    suggestions_table = 'finan.SuggestionsByJournalEntry'
    column_names = "number_with_year entry_date narration "\
                   "accounting_period workflow_buttons *"


class PaymentOrders(FinancialVouchers):
    model = 'finan.PaymentOrder'
    column_names = "number_with_year entry_date narration total "\
                   "execution_date accounting_period workflow_buttons *"
    detail_layout = PaymentOrderDetail()
    suggestions_table = 'finan.SuggestionsByPaymentOrder'


class BankStatements(FinancialVouchers):
    model = 'finan.BankStatement'
    column_names = "number_with_year entry_date balance1 balance2 " \
                   "accounting_period workflow_buttons *"
    detail_layout = 'finan.BankStatementDetail'
    insert_layout = """
    entry_date
    balance1
    """
    suggestions_table = 'finan.SuggestionsByBankStatement'


class AllBankStatements(BankStatements):
    required_roles = dd.login_required(LedgerStaff)


class AllJournalEntries(JournalEntries):
    required_roles = dd.login_required(LedgerStaff)


class AllPaymentOrders(PaymentOrders):
    required_roles = dd.login_required(LedgerStaff)


class PaymentOrdersByJournal(ledger.ByJournal, PaymentOrders):
    pass


class JournalEntriesByJournal(ledger.ByJournal, JournalEntries):
    pass


class BankStatementsByJournal(ledger.ByJournal, BankStatements):
    pass

from lino_xl.lib.ledger.mixins import ItemsByVoucher

# class ItemsByVoucher(ItemsByVoucher):
#     suggest = ShowSuggestions()
#     suggestions_table = None  # 'finan.SuggestionsByJournalEntry'
    # display_mode = 'html'
    # preview_limit = 0
    # label = _("Content")


class ItemsByJournalEntry(ItemsByVoucher):
    model = 'finan.JournalEntryItem'
    column_names = "seqno date partner match account:50 debit credit remark *"
    sum_text_column = 2


class ItemsByBankStatement(ItemsByVoucher):
    model = 'finan.BankStatementItem'
    column_names = "seqno date partner account match remark expense income "\
                   "workflow_buttons *"
    sum_text_column = 2
    suggestions_table = 'finan.SuggestionsByBankStatementItem'
    suggest = ShowSuggestions()


class ItemsByPaymentOrder(ItemsByVoucher):
    model = 'finan.PaymentOrderItem'
    column_names = "seqno partner workflow_buttons bank_account match "\
                   "to_pay remark *"
    suggestions_table = 'finan.SuggestionsByPaymentOrderItem'
    suggest = ShowSuggestions()
    sum_text_column = 1


class FillSuggestionsToVoucher(dd.Action):
    label = _("Fill")
    icon_name = 'lightning'
    http_method = 'POST'
    select_rows = False

    def run_from_ui(self, ar, **kw):
        voucher = ar.master_instance
        seqno = None
        n = 0
        for obj in ar.selected_rows:
            i = voucher.add_item_from_due(obj, seqno=seqno)
            if i is not None:
                # dd.logger.info("20151117 gonna full_clean %s", obj2str(i))
                i.full_clean()
                # dd.logger.info("20151117 gonna save %s", obj2str(i))
                i.save()
                # dd.logger.info("20151117 ok")
                seqno = i.seqno + 1
                n += 1

        msg = _("%d items have been added to %s.") % (n, voucher)
        # logger.info(msg)
        kw.update(close_window=True)
        ar.success(msg, **kw)


class FillSuggestionsToVoucherItem(FillSuggestionsToVoucher):

    def run_from_ui(self, ar, **kw):
        i = ar.master_instance
        obj = ar.selected_rows[0]
        # i is the voucher item from which the suggestion table had
        # been called. obj is the first selected DueMovement object
        # dd.logger.info("20210106 %s", i)
        i.fill_suggestion(obj)
        # for k, v in voucher.due2itemdict(obj).items():
        #     setattr(i, k, v)
        i.full_clean()
        i.save()

        voucher = i.voucher
        seqno = i.seqno
        n = 0
        for obj in ar.selected_rows[1:]:
            i = voucher.add_item_from_due(obj, seqno=seqno)
            if i is not None:
                # dd.logger.info("20151117 gonna full_clean %s", obj2str(i))
                i.on_create(ar)
                i.full_clean()
                # dd.logger.info("20151117 gonna save %s", obj2str(i))
                i.save()
                # dd.logger.info("20151117 ok")
                seqno = i.seqno + 1
                n += 1

        msg = _("%d items have been added to %s.") % (n, voucher)
        # logger.info(msg)
        kw.update(close_window=True)
        ar.success(msg, **kw)


class SuggestionsByVoucher(ledger.ExpectedMovements):

    label = _("Suggestions")
    # column_names = 'partner project match account due_date debts payments balance *'
    column_names = 'info match due_date debts payments balance *'
    window_size = ('90%', 20)  # (width, height)

    editable = False
    auto_fit_column_widths = True
    cell_edit = False

    do_fill = FillSuggestionsToVoucher()

    @classmethod
    def get_dc(cls, ar=None):
        if ar is None:
            raise Exception("20200119 ar is None")
            return None
        voucher = ar.master_instance
        if voucher is None:
            raise Exception("20200119 voucher is None")
            return None
        # return voucher.journal.dc.opposite()  # 20201219 SuggestionsByVoucher.get_dc()
        return voucher.journal.dc  # 20201219 SuggestionsByVoucher.get_dc()

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(SuggestionsByVoucher, cls).param_defaults(ar, **kw)
        voucher = ar.master_instance
        kw.update(for_journal=voucher.journal)
        if not dd.plugins.finan.suggest_future_vouchers:
            kw.update(date_until=voucher.entry_date)
        # kw.update(trade_type=vat.TradeTypes.purchases)
        return kw

    @classmethod
    def get_data_rows(cls, ar, **flt):
        #~ partner = ar.master_instance
        #~ if partner is None: return []
        flt.update(cleared=False)
        # flt.update(account__clearable=True)
        return super(SuggestionsByVoucher, cls).get_data_rows(ar, **flt)


class SuggestionsByJournalEntry(SuggestionsByVoucher):
    master = 'finan.JournalEntry'


class SuggestionsByPaymentOrder(SuggestionsByVoucher):

    master = 'finan.PaymentOrder'
    # column_names = 'partner match account due_date debts payments balance bank_account *'
    column_names = 'info match due_date debts payments balance *'
    quick_search_fields = 'info'

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(SuggestionsByPaymentOrder, cls).param_defaults(ar, **kw)
        voucher = ar.master_instance
        if voucher.journal.sepa_account:
            kw.update(show_sepa=dd.YesNo.yes)
        kw.update(same_dc=dd.YesNo.yes)  # 20201219 SuggestionsByPaymentOrder.param_defaults same_dc
        # kw.update(journal=voucher.journal)
        kw.update(date_until=voucher.execution_date or voucher.entry_date)
        # if voucher.journal.trade_type is not None:
        #     kw.update(trade_type=voucher.journal.trade_type)
        # kw.update(trade_type=vat.TradeTypes.purchases)
        return kw


class SuggestionsByBankStatement(SuggestionsByVoucher):
    master = 'finan.BankStatement'


class SuggestionsByVoucherItem(SuggestionsByVoucher):

    do_fill = FillSuggestionsToVoucherItem()

    @classmethod
    def get_dc(cls, ar=None):
        if ar is None:
            return None
        item = ar.master_instance
        if item is None:
            return None
        # return item.voucher.journal.dc.opposite()  # 20201219 SuggestionsByVoucherItem.get_dc()
        return item.voucher.journal.dc  # 20201219 SuggestionsByVoucherItem.get_dc()

    @classmethod
    def param_defaults(cls, ar, **kw):
        # Note that we skip immeditate parent
        kw = super(SuggestionsByVoucher, cls).param_defaults(ar, **kw)
        item = ar.master_instance
        voucher = item.voucher
        kw.update(for_journal=voucher.journal)
        if not dd.plugins.finan.suggest_future_vouchers:
            kw.update(date_until=voucher.entry_date)
        kw.update(partner=item.partner)
        return kw


class SuggestionsByBankStatementItem(SuggestionsByVoucherItem):
    master = 'finan.BankStatementItem'


class SuggestionsByPaymentOrderItem(SuggestionsByVoucherItem):
    master = 'finan.PaymentOrderItem'


# Declare the voucher types:

VoucherTypes.add_item_lazy(JournalEntriesByJournal)
VoucherTypes.add_item_lazy(PaymentOrdersByJournal)
VoucherTypes.add_item_lazy(BankStatementsByJournal)
# VoucherTypes.add_item_lazy(GroupersByJournal)
