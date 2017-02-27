# Copyright 2008-2016 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.

"""
Model mixins for :mod:`lino_xl.lib.finan`.
"""


from django.db import models
from django.core.exceptions import ValidationError

from lino_xl.lib.excerpts.mixins import Certifiable

from lino_xl.lib.accounts.utils import DEBIT, CREDIT, ZERO
from lino_xl.lib.accounts.fields import DebitOrCreditField
from lino_xl.lib.ledger.mixins import VoucherItem, SequencedVoucherItem
from lino_xl.lib.ledger.mixins import ProjectRelated, Matching
from lino.utils.xmlgen.html import E

from lino.api import dd, rt, _

from lino_xl.lib.ledger.choicelists import VoucherStates

ledger = dd.resolve_app('ledger')


class FinancialVoucher(ledger.Voucher, Certifiable):
    """Base class for all financial vouchers:
    :class:`Grouper`,
    :class:`JournalEntry`,
    :class:`PaymentOrder` and
    :class:`BankStatement`.

    .. attribute:: item_account

        The default value to use when
        :attr:`FinancialVoucherItem.account` of an item is empty.

    .. attribute:: item_remark

        The default value to use when
        :attr:`FinancialVoucherItem.remark` of an item is empty.

    .. attribute:: printed
        See :attr:`lino_xl.lib.excerpts.mixins.Certifiable.printed`

    """

    class Meta:
        abstract = True

    item_account = dd.ForeignKey('accounts.Account', blank=True, null=True)
    item_remark = models.CharField(
        _("External reference"), max_length=200, blank=True)

    # def after_state_change(self, ar, old, new):
    #     super(FinancialVoucher, self).after_state_change(ar, old, new)
    #     if self.journal.auto_check_clearings:
    #         self.check_clearings()

    def add_item_from_due(self, obj, **kwargs):
        # if not obj.balance:
        #     raise Exception("20151117")
        if obj.project:
            kwargs.update(project=obj.project)
        if obj.partner:
            kwargs.update(partner=obj.partner)
        dc = not obj.dc
        # if self.journal.invert_due_dc:
        #     dc = not obj.dc
        # else:
        #     dc = obj.dc
        i = self.add_voucher_item(
            obj.account, dc=dc,
            amount=obj.balance, match=obj.match, **kwargs)
        if i.amount < 0:
            i.amount = - i.amount
            i.dc = not i.dc
        return i

    def get_wanted_movements(self):
        raise NotImplemented()

    def get_finan_movements(self):
        """Yield the movements to be booked for this finanical voucher.

        This method is expected to return a tuple ``(amount,
        movements_and_items)``, where `amount` is the total amount and
        `movements_and_items` is a sequence of tuples ``(mvt, item)``
        where `mvt` is a :class:`Movement` object to be saved and
        `item` it the (existing) voucher item which caused this
        movement.

        """
        # dd.logger.info("20151211 get_finan_movements()")
        amount = ZERO
        movements_and_items = []
        for i in self.items.all():
            if i.dc == self.journal.dc:
                amount += i.amount
            else:
                amount -= i.amount
            # kw = dict(seqno=i.seqno, partner=i.partner)
            kw = dict(partner=i.get_partner())
            kw.update(match=i.match or i.get_default_match())
            b = self.create_movement(
                i, i.account or self.item_account,
                i.project, i.dc, i.amount, **kw)
            movements_and_items.append((b, i))

        return amount, movements_and_items


class FinancialVoucherItem(VoucherItem, SequencedVoucherItem,
                           ProjectRelated, Matching):
    """The base class for the items of all types of financial vouchers
    (:class:`FinancialVoucher`).

    .. attribute:: account

        The general account to be used in the primary booking.
        If this is empty, use :attr:`item_account` of the voucher.

    .. attribute:: project

        The client related to this transaction.

    .. attribute:: partner

        The partner account to be used in the primary booking.
    
        In Lino Welfare this field is optional and used only for
        transactions whose *recipient* is different from the *client*.
        When empty, Lino will book to the **client**
        (i.e. :attr:`project`).

    .. attribute:: amount

        The amount to be booked. If this is empty, then the voucher
        cannot be registered.

    .. attribute:: dc

        The direction of the primary booking to create.

    .. attribute:: remark

        External reference. The description of this transation
        as seen by the external partner.

    .. attribute:: seqno

    .. attribute:: match

        An arbitrary string used to group several movements.

        A reference to the voucher that caused this voucher entry.  For
        example the :attr:`match` of the payment of an invoice points
        to that invoice.

    """
    class Meta:
        abstract = True
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    amount = dd.PriceField(_("Amount"), default=ZERO, null=False)
    dc = DebitOrCreditField()
    remark = models.CharField(
        _("External reference"), max_length=200, blank=True)
    account = dd.ForeignKey('accounts.Account', blank=True, null=True)
    partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)

    @dd.chooser(simple_values=True)
    def match_choices(cls, voucher, partner):
        return cls.get_match_choices(voucher.journal, partner)

    def get_default_match(self):
        """The string to use as `match` when no explicit match is specified on
        this voucher.

        """
        return "%s %s:%s" % (
            self.voucher.journal.ref, self.voucher.number, self.seqno)
        # return str(self.date)

    def get_siblings(self):
        return self.voucher.items.all()

    def unused_match_changed(self, ar):
        if self.match:
            get_due_movements(not self.voucher.journal.dc)
            dc = not self.voucher.journal.dc
            m = ledger.DueMovement(dc, self)
            # dd.logger.info("20160604 %s %s", m.debts, m.payments)
            self.dc = dc
            self.amount = m.balance
            # if not m.balance:
            #     raise Exception("20151117")

    def partner_changed(self, ar):
        """The :meth:`trigger method <lino.core.model.Model.FOO_changed>` for
        :attr:`partner`.

        """
        # dd.logger.info("20160329 FinancialMixin.partner_changed")
        if not self.partner:
            return
        flt = dict(partner=self.partner, cleared=False)

        if not dd.plugins.finan.suggest_future_vouchers:
            flt.update(value_date__lte=self.voucher.voucher_date)

        if self.match:
            flt.update(match=self.match)
        suggestions = list(ledger.get_due_movements(
            self.voucher.journal.dc, **flt))

        if len(suggestions) == 0:
            pass
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

    def account_changed(self, ar):
        if not self.account:
            return
        if self.account.default_amount:
            self.amount = self.account.default_amount
            self.dc = not self.account.type.dc
        
    def get_partner(self):
        return self.partner or self.project

    def fill_suggestion(self, match):
        """Fill the fields of this item from the given suggestion (a
        `DueMovement` instance).

        """
        # if not match.balance:
        #     raise Exception("20151117")
        if match.trade_type:
            self.account = match.trade_type.get_partner_account()
        if self.account_id is None:
            self.account = match.account
        self.dc = match.dc
        self.amount = - match.balance
        self.match = match.match
        self.project = match.project

    def guess_amount(self):
        self.account_changed(None)
        if self.amount is not None:
            return
        self.partner_changed(None)
        if self.amount is not None:
            return
        self.amount = ZERO

    def full_clean(self, *args, **kwargs):
        # if self.amount is None:
        #     if self.account and self.account.default_amount:
        #         self.amount = self.account.default_amount
        #         self.dc = self.account.type.dc
        #     else:
        #         self.amount = ZERO
        if self.dc is None:
            # self.dc = not self.voucher.journal.dc
            if self.account is None:
                self.dc = not self.voucher.journal.dc
            else:
                self.dc = not self.account.type.dc
        if self.amount is None:
            # amount can be None e.g. if user entered ''
            self.guess_amount()
        elif self.amount < 0:
            self.amount = - self.amount
            self.dc = not self.dc
        # dd.logger.info("20151117 FinancialVoucherItem.full_clean a %s", self.amount)
        super(FinancialVoucherItem, self).full_clean(*args, **kwargs)
        # dd.logger.info("20151117 FinancialVoucherItem.full_clean b %s", self.amount)


class DatedFinancialVoucher(FinancialVoucher):
    """A :class:`FinancialVoucher` whose items have a :attr:`date` field.
    """
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
    """A :class:`FinancialVoucherItem` with an additional :attr:`date`
    field.

    .. attribute:: date

        The value date of this item.

    """
    class Meta:
        app_label = 'finan'
        abstract = True

    date = models.DateField(blank=True, null=True)

    def on_create(self, ar):
        super(DatedFinancialVoucherItem, self).on_create(ar)
        if self.voucher.last_item_date:
            self.date = self.voucher.last_item_date
        else:
            self.date = dd.today()

    def date_changed(self, ar):
        obj = self.voucher
        if obj.last_item_date != self.date:
            obj.last_item_date = self.date
            obj.full_clean()
            obj.save()


