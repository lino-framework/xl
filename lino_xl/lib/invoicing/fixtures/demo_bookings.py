# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
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

"""Creates montly invoicing plans and executes them.

dd.plugins.ledger.start_year

first ten items
(i.e. generates ten invoices).

"""
import datetime
from lino_xl.lib.cal.choicelists import DurationUnits
from lino.api import dd, rt


def objects():
    # vt = dd.plugins.invoicing.get_voucher_type()
    # jnl_list = vt.get_journals()
    # if len(jnl_list) == 0:
    #     return
    from lino_xl.lib.ledger.roles import LedgerStaff
    accountants = LedgerStaff.get_user_profiles()
    users = rt.models.users.User.objects.filter(
        language=dd.get_default_language(), user_type__in=accountants)
    if users.count() == 0:
        return
    ses = rt.login(users[0].username)
    Plan = rt.modules.invoicing.Plan

    # we don't write invoices the last two months because we want to
    # have something in our invoicing plan.
    today = datetime.date(dd.plugins.ledger.start_year, 1, 1)
    while today < dd.demo_date(-60):
        plan = Plan.start_plan(ses.get_user(), today=today)
        yield plan
        plan.fill_plan(ses)
        # for i in plan.items.all()[:9]:
        for i in plan.items.all():
            obj = i.create_invoice(ses)
            assert obj is not None
            yield obj
        today = DurationUnits.months.add_duration(today, 1)
