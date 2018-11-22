# -*- coding: UTF-8 -*-# Copyright 2012-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""User interface for this plugin.

"""

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

"""Database models for :mod:`lino_xl.lib.meeting`.

.. autosummary::

"""

import logging

logger = logging.getLogger(__name__)

from decimal import Decimal

ZERO = Decimal()
ONE = Decimal(1)

from django.db import models
from django.db.models import Q
from django.conf import settings

from lino.api import dd, rt, _
from lino import mixins

from lino.core.roles import Explorer
from lino.modlib.office.roles import OfficeUser
from lino.utils import join_elems
from etgen.html import E
from lino.utils.mti import get_child
from lino.utils.report import Report

from lino.modlib.system.choicelists import PeriodEvents
from lino.modlib.users.mixins import My

from lino_xl.lib.lists.models import MembersByList

from .choicelists import MeetingStates

class MeetingDetail(dd.DetailLayout):
        """Customized detail_layout for neeting.
        """
        main = "general #cal_tab more"

        general = dd.Panel("""
        room site workflow_buttons #name ref
        deploy.DeploymentsByMilestone
        """, label=_("General"))

        cal_tab = dd.Panel("""
        start_date end_date start_time end_time
        max_events max_date every_unit every
        monday tuesday wednesday thursday friday saturday sunday
        cal.EntriesByController
        """, label=_("Calendar"))

        more_left = """
        id:8
        name
        user
        """

        more = dd.Panel("""
        more_left:30 #blogs.EntriesByController:50
        description     stars.StarsByController:30
        """, label=_("More"))


class Meetings(dd.Table):
    """Base table for all Meetings.
    """
    required_roles = dd.login_required((OfficeUser,))
    model = 'meetings.Meeting'
    detail_layout = MeetingDetail()
    insert_layout = dd.InsertLayout("""name
    ref room
    start_date
    """, window_size = (40, 10,))
    column_names = "start_date name ref site room workflow_buttons *"
    # order_by = ['start_date']
    # order_by = 'line__name room__name start_date'.split()
    # order_by = ['name']
    order_by = ['-start_date', '-start_time']
    auto_fit_column_widths = True


    parameters = mixins.ObservedDateRange(
        user=dd.ForeignKey(
            settings.SITE.user_model,
            blank=True, null=True),
        show_active=dd.YesNo.field(
            _("Active"), blank=True,
            help_text=_("Whether to show rows in some active state")),
        state=MeetingStates.field(blank=True),
        member=dd.ForeignKey(dd.resolve_model('contacts.Partner'),
            verbose_name=_("Member"), blank=True,
            help_text=_("Show rows that this person is a member")),
    )
    params_layout = """user room state show_active member
    start_date end_date """

    # simple_parameters = 'line teacher state user'.split()

    @classmethod
    def create_instance(self, ar, **kw):
        # dd.logger.info("20160714 %s", kw)
        obj = super(Meetings, self).create_instance(ar, **kw)
        # if self._course_area is not None:
        #     obj.course_area = self._course_area
        return obj

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        # dd.logger.info("20160223 %s", self)
        qs = super(Meetings, self).get_request_queryset(ar, **kwargs)
        if isinstance(qs, list):
            return qs
        pv = ar.param_values

        qs = self.model.add_param_filter(
            qs, show_active=pv.show_active)

        if pv.state:
            qs = qs.filter(state=pv.state)

        if pv.member:
            sqs = rt.models.stars.Star.for_model('meetings.Meeting', user=pv.member)
            stared_ticket_ids = sqs.values_list('owner_id')
            qs = qs.filter(pk__in=stared_ticket_ids)

        if pv.start_date:
            # dd.logger.info("20160512 start_date is %r", pv.start_date)
            qs = PeriodEvents.started.add_filter(qs, pv)
            # qs = qs.filter(start_date__gte=pv.start_date)
        if pv.end_date:
            qs = PeriodEvents.ended.add_filter(qs, pv)
            # qs = qs.filter(end_date__lte=pv.end_date)
        # dd.logger.info("20160512 %s", qs.query)
        return qs


class AllMeetings(Meetings):
    required_roles = dd.login_required(Explorer)
    column_names = "start_date:8 room user name ref *"
                   # "weekdays_text:10 times_text:10"

class MyMeetings(Meetings):
    column_names = "start_date:8 overview site room workflow_buttons *"
    order_by = ['start_date']

    @classmethod
    def get_actor_label(self):
        return self._label or \
            _("My %s") % self.model._meta.verbose_name_plural

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyMeetings, self).param_defaults(ar, **kw)
        # kw.update(state=MeetingStates.active)
        kw.update(show_active=dd.YesNo.yes)
        kw.update(member=ar.get_user())
        return kw


class ActiveMeetings(Meetings):
    label = _("Future Meetings")
    column_names = 'overview room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(ActiveMeetings, self).param_defaults(ar, **kw)
        # kw.update(state=MeetingStates.active
        kw.update(show_active=dd.YesNo.yes)
        # kw.update(can_enroll=dd.YesNo.yes)
        return kw

class MeetingsBySite(ActiveMeetings):
    label = _("Site Milestones")
    column_names = 'overview *'
    master_key = 'site'


class InactiveMeetings(Meetings):
    label = _("Inactive Meetings")
    column_names = 'overview room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(InactiveMeetings, self).param_defaults(ar, **kw)
        kw.update(state=MeetingStates.inactive)
        return kw

#
# class ClosedCourses(Activities):
#     label = _("Closed courses")
#     column_names = 'overview enrolments:8 room *'
#     hide_sums = True
#
#     @classmethod
#     def param_defaults(self, ar, **kw):
#         kw = super(ClosedCourses, self).param_defaults(ar, **kw)
#         kw.update(state=CourseStates.closed)
#         return kw

# class MembersByMeeting(MembersByList):
#     master = "meetings.Meeting"
#     master_key = None
#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         if ar.master_instance is None:
#             return
#         kw.update(list = ar.master_instance.list)
#         return kw
