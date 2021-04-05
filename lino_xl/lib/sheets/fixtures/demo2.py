# -*- coding: UTF-8 -*-
# Copyright 2018-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Create a series of reports.

All reports have the same user, which would not be possible when using the web
front end because reports are user plans and you can have only one plan per
user. But programatically it is possible and doesn't disturb.

"""

from lino.api import rt, dd


def objects():
    # dd.logger.info(
    #     "sheets %s %s",
    #     dd.plugins.ledger.start_year, dd.today().year+1)
    from datetime import date
    Report = rt.models.sheets.Report
    AccountingPeriod = rt.models.ledger.AccountingPeriod
    ses = rt.login("robin")
    for year in range(dd.plugins.ledger.start_year, dd.today().year+1):
        sp = AccountingPeriod.get_default_for_date(date(year, 1, 1))
        ep = AccountingPeriod.get_default_for_date(date(year, 12, 31))
        obj = Report(start_period=sp, end_period=ep, user=ses.get_user())
        yield obj
        obj.run_update_plan(ses)
        # dd.logger.info("20180907 %s", year)
