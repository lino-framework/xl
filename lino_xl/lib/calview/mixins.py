# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd

class Plannable(dd.Model):
    class Meta:
        abstract = True

    def get_weekly_chunks(obj, ar, qs, current_week_day):
        return [e.obj2href(ar, e.colored_calendar_fmt(ar.param_values)) for e in qs]
