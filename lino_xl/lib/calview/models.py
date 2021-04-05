# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.mixins import BabelDesignated, Sequenced
from lino.api import dd, rt, _

from .mixins import Plannable, Planners


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

    # def get_weekly_chunks(obj, ar, qs, today):
    #     if obj.start_time:
    #         qs = qs.filter(start_time__gte=obj.start_time,
    #                        start_time__isnull=False)
    #     if obj.end_time:
    #         qs = qs.filter(start_time__lt=obj.end_time,
    #                        start_time__isnull=False)
    #     return [e.obj2href(ar, ar.actor.get_calview_div(e, ar)) for e in qs]
    #
    @classmethod
    def get_plannable_entries(cls, obj, qs, ar):
        # qs = rt.models.cal.Event.objects.all()
        if obj is cls.HEADER_ROW:
            return qs.filter(start_time__isnull=True)
        if obj.start_time:
            return qs.filter(start_time__gte=obj.start_time,
                             start_time__isnull=False)
        if obj.end_time:
            return qs.filter(start_time__lt=obj.end_time,
                             start_time__isnull=False)
        return qs

dd.update_field(DailyPlannerRow, 'overview', verbose_name=_("Time range"))

from .ui import *

# DailyPlannerRow.install_actors(globals())
