# -*- coding: UTF-8 -*-
# Copyright 2016-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import datetime
from lino_xl.lib.cal.choicelists import DurationUnits
from lino.api import dd, rt

Plan = rt.models.invoicing.Plan
Area = rt.models.invoicing.Area


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
    ses = rt.login(users.first().username)

    for area in Area.objects.all():
        today = datetime.date(dd.plugins.ledger.start_year, 1, 1)
        while today < dd.demo_date(-60):
            plan = Plan.run_start_plan(ses.get_user(), today=today, area=area)
            yield plan
            plan.fill_plan(ses)
            # for i in plan.items.all()[:9]:
            for i in plan.items.all():
                obj = i.create_invoice(ses)
                if obj is not None:
                    yield obj
                else:
                    msg = "create_invoice failed for {}".format(i)
                    raise Exception(msg)
                    # dd.logger.warning(msg)
                    # return
            today = DurationUnits.months.add_duration(today, 1)
