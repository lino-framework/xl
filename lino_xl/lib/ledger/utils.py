# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Utilities for this plugin.


.. data:: on_ledger_movement

    Sent when a partner has had at least one change in a ledger movement.
    
    - `sender`   the database model
    - `instance` the partner



"""

from builtins import str
from decimal import Decimal, ROUND_HALF_UP
from django.dispatch import Signal, receiver
from lino.api import rt, dd

from lino.utils import SumCollector
from lino_xl.lib.accounts.utils import Balance, ZERO, DEBIT


CENT = Decimal('.01')

on_ledger_movement = Signal(['instance'])


def myround(d):
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


class DueMovement(object):
    def __init__(self, dc, mvt):
        self.dc = dc
        # self.match = mvt.get_match()
        self.match = mvt.match
        self.partner = mvt.partner
        self.account = mvt.account
        self.project = mvt.project
        self.pk = self.id = mvt.id
        self.obj2href = mvt.obj2href

        self.debts = []
        self.payments = []
        self.balance = ZERO
        self.due_date = None
        self.trade_type = None
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
        """Add the given movement to the list of movements that are being
        cleared by this DueMovement.

        """
        # dd.logger.info("20160604 collect %s", mvt)
        if mvt.cleared:
            self.has_satisfied_movement = True
        else:
            self.has_unsatisfied_movement = True

        voucher = mvt.voucher.get_mti_leaf()
        due_date = voucher.get_due_date()
        if self.due_date is None or due_date < self.due_date:
            self.due_date = due_date
            
        if self.trade_type is None:
            self.trade_type = voucher.get_trade_type()
        if mvt.dc == self.dc:
            self.debts.append(mvt)
            self.balance += mvt.amount
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
            self.balance -= mvt.amount

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


def get_due_movements(dc, **flt):
    """Analyze the movements corresponding to the given filter condition
    `flt` and yield a series of :class:`DueMovement` objects which
    --if they were booked-- would satisfy the given movements.

    This is the data source for :class:`ExpectedMovements
    <lino_xl.lib.ledger.ui.ExpectedMovements>` and subclasses.
    
    There will be at most one :class:`DueMovement` per (account,
    partner, match), each of them grouping the movements with same
    partner, account and match.

    The balances of the :class:`DueMovement` objects will be positive
    or negative depending on the specified `dc`.

    Generates and yields a list of the :class:`DueMovement` objects
    specified by the filter criteria.

    Arguments:

    :dc: (boolean): The caller must specify whether he means the debts
         and payments *towards the partner* or *towards myself*.

    :flt: Any keyword argument is forwarded to Django's `filter()
          <https://docs.djangoproject.com/en/dev/ref/models/querysets/#filter>`_
          method in order to specifiy which :class:`Movement` objects
          to consider.

    """
    if dc is None:
        return
    qs = rt.models.ledger.Movement.objects.filter(**flt)
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
        # matches = matches_by_account.setdefault(k, set())
        # m = mvt.match or mvt
        # if m not in matches:
        #     matches.add(m)
        #     yield DueMovement(dc, mvt)
    return matches


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
    """Check whether involved movements are cleared or not, and update
    their :attr:`cleared` field accordingly.

    """
    qs = qs.select_related('voucher', 'voucher__journal')
    if len(matches):
        qs = qs.filter(match__in=matches)
    sums = SumCollector()
    for mvt in qs:
        # k = (mvt.get_match(), mvt.account)
        k = (mvt.match, mvt.account)
        mvt_dc = mvt.dc
        # if mvt.voucher.journal.invert_due_dc:
        #     mvt_dc = mvt.dc
        # else:
        #     mvt_dc = not mvt.dc
        if mvt_dc == DEBIT:
            sums.collect(k, mvt.amount)
        else:
            sums.collect(k, - mvt.amount)

    for k, balance in sums.items():
        match, account = k
        sat = (balance == ZERO)
        qs.filter(account=account, match=match).update(cleared=sat)

