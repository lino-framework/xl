# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)


"""Database models for this plugin.
"""

from __future__ import unicode_literals


from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from lino import mixins
from lino.modlib.users.mixins import UserAuthored

from .roles import TrendsStaff, TrendsUser


class TrendArea(mixins.BabelNamed):

    """Represents a possible choice for the `trend_area` field of a
    :class:`TrendStage`.

    """

    class Meta:
        app_label = 'trends'
        abstract = dd.is_abstract_model(__name__, 'TrendArea')
        verbose_name = _("Trend area")
        verbose_name_plural = _("Trend areas")


class TrendAreas(dd.Table):
    required_roles = dd.login_required(TrendsStaff)
    model = 'trends.TrendArea'
    column_names = 'name *'
    detail_layout = """
    id name
    StagesByArea
    """


class TrendStage(mixins.BabelNamed, mixins.Referrable):

    class Meta:
        app_label = 'trends'
        abstract = dd.is_abstract_model(__name__, 'TrendStage')
        verbose_name = _("Trend stage")
        verbose_name_plural = _("Trend stages")

    trend_area = dd.ForeignKey('trends.TrendArea', blank=True, null=True)


class TrendStages(dd.Table):
    required_roles = dd.login_required(TrendsUser)
    model = 'trends.TrendStage'
    column_names = 'ref trend_area name *'
    order_by = ['ref']
    stay_in_grid = True

    insert_layout = """
    name
    ref trend_area
    """

    detail_layout = dd.DetailLayout("""
    ref trend_area id
    name
    EventsByStage
    """)

class StagesByArea(TrendStages):
    master_key = 'trend_area'
    column_names = "ref name *"


class TrendEvent(UserAuthored):

    class Meta:
        app_label = 'trends'
        abstract = dd.is_abstract_model(__name__, 'TrendEvent')
        verbose_name = _("Trend event")
        verbose_name_plural = _("Trend events")
        # unique_together = ['subject', 'trend_stage']

    subject = dd.ForeignKey(
        dd.plugins.trends.subject_model,
        related_name="trend_events")
    event_date = models.DateField(_("Date"), default=dd.today)
    trend_area = dd.ForeignKey('trends.TrendArea')
    trend_stage = dd.ForeignKey(
        'trends.TrendStage', blank=True, null=True)
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    @dd.chooser()
    def trend_stage_choices(self, trend_area):
        if not trend_area:
            return rt.models.trends.TrendStage.objects.none()
        return rt.models.trends.TrendStage.objects.filter(
            trend_area=trend_area)


class TrendEvents(dd.Table):
    required_roles = dd.login_required(TrendsUser)
    model = 'trends.TrendEvent'
    order_by = ['event_date', 'id']
        

class EventsByStage(TrendEvents):
    label = _("Trend events")
    master_key = 'trend_stage'
    column_names = "event_date subject remark * subject__*"


class EventsBySubject(TrendEvents):
    master_key = 'subject'
    column_names = "event_date trend_area trend_stage remark *"


class AllTrendEvents(TrendEvents):
    required_roles = dd.login_required(TrendsStaff)


