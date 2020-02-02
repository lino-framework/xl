# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.mixins import BabelDesignated, Sequenced
from lino.api import dd, rt, _

from .mixins import Plannable

class DailyPlannerRow(BabelDesignated, Sequenced, Plannable):

    class Meta:
        app_label = 'calview'
        abstract = dd.is_abstract_model(__name__, 'PlannerRow')
        verbose_name = _("Planner row")
        verbose_name_plural = _("Planner rows")
        ordering = ['start_time','-seqno']

    start_time = dd.TimeField(
        blank=True, null=True,
        verbose_name=_("Start time"))
    end_time = dd.TimeField(
        blank=True, null=True,
        verbose_name=_("End time"))

    def get_weekly_chunks(obj, ar, qs, today):
        if obj.start_time:
            qs = qs.filter(start_time__gte=obj.start_time,
                           start_time__isnull=False)
        if obj.end_time:
            qs = qs.filter(start_time__lt=obj.end_time,
                           start_time__isnull=False)
        return [e.obj2href(ar, e.colored_calendar_fmt(ar.param_values)) for e in qs]


dd.update_field(DailyPlannerRow, 'overview', verbose_name=_("Time range"))

from .ui import *
