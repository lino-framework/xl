# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino import mixins
from lino.api import dd, _

class DailyPlannerRow(mixins.BabelDesignated, mixins.Sequenced):

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

dd.update_field(DailyPlannerRow, 'overview', verbose_name=_("Time range"))

from .ui import *
