# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
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


"""Utilities for `lino_xl.lib.ledger`


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
from lino_xl.lib.accounts.utils import ZERO, DEBIT


CENT = Decimal('.01')

on_ledger_movement = Signal(['instance'])


def myround(d):
    return d.quantize(CENT, rounding=ROUND_HALF_UP)


class Balance(object):
    """Light-weight object to represent a balance, i.e. an amount together
    with its booking direction (debit or credit).

    Attributes:

    .. attribute:: d

        The amount of this balance when it is debiting, otherwise zero.

    .. attribute:: c

        The amount of this balance when it is crediting, otherwise zero.

    """

    def __init__(self, d, c):
        if d > c:
            self.d = d - c
            self.c = ZERO
        else:
            self.c = c - d
            self.d = ZERO


class DueMovement(object):
    """
    A volatile object representing a group of matching movements.

    A **due movement** is a movement which a partner should do in
    order to satisfy their debt.  Or which we should do in order to
    satisfy our debt towards a partner.

    The "matching" movements of a given movement are those whose
    `match`, `partner` and `account` fields have the same values.
    
    These movements are themselves grouped into "debts" and "payments".
    A "debt" increases the debt and a "payment" decreases it.
    
    .. attribute:: match

        The common `match` string of these movments

    .. attribute:: dc

        Whether I mean *my* debts and payments (towards that partner)
        or those *of the partner* (towards me).

    .. attribute:: partner

    .. attribute:: account

    """
    def __init__(self, dc, mvt):
        self.dc = dc
        # self.match = mvt.get_match()
        self.match = mvt.match
        self.partner = mvt.partner
        self.account = mvt.account
        self.project = mvt.project
        self.pk = self.id = mvt.id

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
        # qs = rt.modules.ledger.Movement.objects.filter(**flt)
        # for mvt in qs.order_by('voucher__date'):
        #     self.collect(mvt)

    def __repr__(self):
        return "{0} {1} {2}".format(
            dd.obj2str(self.partner), self.match, self.balance)

    def collect_all(self):
        flt = dict(
            partner=self.partner, account=self.account, match=self.match)
        for mvt in rt.modules.ledger.Movement.objects.filter(**flt):
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
    qs = rt.modules.ledger.Movement.objects.filter(**flt)
    qs = qs.filter(account__clearable=True)
    # qs = qs.exclude(match='')
    qs = qs.order_by('value_date')
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


def check_clearings(partner, matches=[]):
    """Check whether involved movements are cleared or not, and update
    their :attr:`cleared` field accordingly.

    """
    qs = rt.modules.ledger.Movement.objects.filter(
        partner=partner, account__clearable=True).order_by('match')
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

    on_ledger_movement.send(sender=partner.__class__, instance=partner)
