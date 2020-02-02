# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _


def objects():

    DPR = rt.models.calview.DailyPlannerRow
    yield DPR(end_time="12:00", **dd.str2kw('designation', _("AM")))
    yield DPR(start_time="12:00", **dd.str2kw('designation', _("PM")))
    # yield DPR(**dd.str2kw('designation', _("All day")))
