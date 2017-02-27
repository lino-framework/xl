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


"""Creates fictive demo bookings to monthly payment orders and bank
statements.  Bank statements of last month are not yet entered into
database

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


import datetime
from dateutil.relativedelta import relativedelta as delta

from decimal import Decimal

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

finan = dd.resolve_app('finan')

REQUEST = settings.SITE.login()  # BaseRequest()
MORE_THAN_A_MONTH = datetime.timedelta(days=40)

# most payments are arriving as suggested, i.e. the customer pays the
# full ammount. But there are exceptions: 5% discount taken at
# payment, no payment a t all, partly payments of 70%, or (very
# accidentally) 2% too much.

PAYMENT_DIFFS = [None] * 4
PAYMENT_DIFFS += [-0.05]
PAYMENT_DIFFS += [None] * 3
PAYMENT_DIFFS += [-1.00]
PAYMENT_DIFFS += [None] * 2
PAYMENT_DIFFS += [-0.30]
PAYMENT_DIFFS += [0.02]
PAYMENT_DIFFS = Cycler(PAYMENT_DIFFS)


def objects(refs="PMO BNK"):

    Journal = rt.modules.ledger.Journal
    USERS = Cycler(settings.SITE.user_model.objects.all())
    OFFSETS = Cycler(12, 20, 28)

    START_YEAR = dd.plugins.ledger.start_year
    end_date = settings.SITE.demo_date(-30)

    for ref in refs.split():
        offset = OFFSETS.pop()
        date = datetime.date(START_YEAR, 1, 1)
        jnl = Journal.objects.get(ref=ref)
        sug_table = jnl.voucher_type.table_class.suggestions_table
        while date < end_date:
            voucher = jnl.create_voucher(
                user=USERS.pop(),
                voucher_date=date + delta(days=offset))
            yield voucher

            # start action request for do_fill:
            ba = sug_table.get_action_by_name('do_fill')
            ar = ba.request(master_instance=voucher)
            # select all rows:
            suggestions = sug_table.request(voucher)
            ar.selected_rows = list(suggestions)
            # run the action:
            ar.run()

            # some items differ from what was suggested:
            if ref == 'BNK':
                for item in voucher.items.all():
                    pd = PAYMENT_DIFFS.pop()
                    if pd:
                        pd = Decimal(pd)
                        item.amount += item.amount * pd
                        if item.amount:
                            item.save()
                        else:
                            item.delete()
            # if no items have been created (or if they have been
            # deleted by PAYMENT_DIFFS), remove the empty voucher:
            if voucher.items.count() == 0:
                voucher.delete()
            else:
                voucher.register(REQUEST)
                voucher.save()

            date += delta(months=1)

        # JOURNAL_BANK = Journal.objects.get(ref="BNK")
        # bs = JOURNAL_BANK.create_voucher(
        #     user=USERS.pop(),
        #     date=date + delta(days=28))
        # yield bs
        # suggestions = finan.SuggestionsByBankStatement.request(bs)
        # ba = suggestions.actor.get_action_by_name('do_fill')
        # ar = ba.request(master_instance=bs)
        # ar.selected_rows = [x for x in suggestions]
        # ar.run()
        # bs.register(REQUEST)
        # bs.save()

