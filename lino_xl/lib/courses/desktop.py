# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import logging
logger = logging.getLogger(__name__)

from decimal import Decimal
ZERO = Decimal()
ONE = Decimal(1)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.text import format_lazy

from lino.api import dd, rt, _
from lino import mixins

from lino.core.roles import Explorer
from lino.utils import join_elems
from etgen.html import E
from lino.utils.mti import get_child
from lino.utils.report import Report

from lino.modlib.system.choicelists import PeriodEvents
from lino.modlib.users.mixins import My

from .choicelists import EnrolmentStates, CourseStates, CourseAreas

from .roles import CoursesUser, CoursesTeacher

cal = dd.resolve_app('cal')

try:
    teacher_model = dd.plugins.courses.teacher_model
    teacher_label = dd.plugins.courses.teacher_label
    pupil_model = dd.plugins.courses.pupil_model
except AttributeError:
    # Happens only when Sphinx autodoc imports it and this module is
    # not installed.
    teacher_label = _("Instructor")
    teacher_model = 'foo.Bar'
    pupil_model = 'foo.Bar'

FILL_EVENT_GUESTS = False


class Slots(dd.Table):
    model = 'courses.Slot'
    required_roles = dd.login_required(dd.SiteAdmin)
    insert_layout = """
    start_time end_time
    name
    """
    detail_layout = """
    name start_time end_time
    courses.CoursesBySlot
    """


class Topics(dd.Table):
    model = 'courses.Topic'
    required_roles = dd.login_required(dd.SiteAdmin)
    stay_in_grid = True
    detail_layout = """
    id name
    courses.LinesByTopic
    courses.CoursesByTopic
    """
    # insert_layout = """
    # name
    # id
    # """


class Lines(dd.Table):
    model = 'courses.Line'
    required_roles = dd.login_required(CoursesUser)
    column_names = ("ref name topic course_area "
                    "event_type guest_role every_unit every *")
    order_by = ['ref', 'name']
    detail_layout = """
    id name ref
    company contact_person
    course_area topic fees_cat fee options_cat body_template
    event_type guest_role every_unit every
    excerpt_title
    description
    # courses.CoursesByLine
    """
    insert_layout = dd.InsertLayout("""
    name
    ref topic
    every_unit every event_type
    description
    """, window_size=(70, 16))


class LinesByTopic(Lines):
    master_key = "topic"


class EntriesByTeacher(cal.Events):
    "Show calendar entries of activities led by this teacher"
    
    master = teacher_model
    column_names = 'when_text:20 owner room state'
    # column_names = 'when_text:20 course__line room state'
    auto_fit_column_widths = True

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        teacher = ar.master_instance
        if teacher is None:
            return []
        if True:
            return []
        # TODO: build a list of courses, then show entries by course
        qs = super(EntriesByTeacher, self).get_request_queryset(ar, **kwargs)
        # mycourses = rt.models.Course.objects.filter(teacher=teacher)
        qs = qs.filter(course__in=teacher.course_set.all())
        return qs


class CourseDetail(dd.DetailLayout):
    required_roles = dd.login_required((CoursesUser, CoursesTeacher))
    # start = "start_date start_time"
    # end = "end_date end_time"
    # freq = "every every_unit"
    # start end freq
    
    main = "general cal_tab enrolments"
    
    general = dd.Panel("""
    line teacher start_date start_time end_time end_date
    room #slot workflow_buttons id:8 user
    name
    description
    """, label=_("General"))
    
    cal_tab = dd.Panel("""
    max_events max_date every_unit every
    monday tuesday wednesday thursday friday saturday sunday
    cal.EntriesByController
    """, label=_("Calendar"))

    enrolments_top = 'enrolments_until max_places:10 confirmed free_places:10 print_actions:15'

    enrolments = dd.Panel("""
    enrolments_top
    EnrolmentsByCourse
    """, label=_("Enrolments"))

# Course.detail_layout_class = CourseDetail

class Activities(dd.Table):
    _course_area = None
    required_roles = dd.login_required((CoursesUser, CoursesTeacher))
    model = 'courses.Course'
    detail_layout = 'courses.CourseDetail'
    insert_layout = """
    line teacher
    name start_date
    """
    column_names = "start_date name line teacher room workflow_buttons *"
    # order_by = ['start_date']
    # order_by = 'line__name room__name start_date'.split()
    # order_by = ['name']
    order_by = ['-start_date', '-start_time']
    auto_fit_column_widths = True

    parameters = mixins.ObservedDateRange(
        line=dd.ForeignKey('courses.Line', blank=True, null=True),
        topic=dd.ForeignKey('courses.Topic', blank=True, null=True),
        teacher=dd.ForeignKey(
            teacher_model, verbose_name=teacher_label,
            blank=True, null=True),
        # user=dd.ForeignKey(
        #     settings.SITE.user_model,
        #     blank=True, null=True),
        show_exposed=dd.YesNo.field(
            _("Exposed"), blank=True,
            help_text=_("Whether to show rows in an exposed state")),
        state=CourseStates.field(blank=True),
        can_enroll=dd.YesNo.field(blank=True),
    )

    params_layout = """topic line user teacher state 
    room can_enroll:10 start_date end_date show_exposed"""

    # simple_parameters = 'line teacher state user'.split()

    @dd.chooser()
    def line_choices(cls):
        # dd.logger.info("20181104 line_choices %s", cls)
        qs = rt.models.courses.Line.objects.all()
        if cls._course_area:
            qs = qs.filter(course_area=cls._course_area)
        return qs

    @classmethod
    def create_instance(cls, ar, **kw):
        # dd.logger.info("20160714 %s", kw)
        obj = super(Activities, cls).create_instance(ar, **kw)
        if cls._course_area is not None:
            obj.course_area = cls._course_area
            qs = rt.models.courses.Line.objects.filter(
                course_area=cls._course_area)
            if qs.count() == 1:
                obj.line = qs[0]
        return obj

    @classmethod
    def get_actor_label(self):
        if self._course_area is not None:
            return self._course_area.text
        return super(Activities, self).get_actor_label()

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(Activities, cls).get_simple_parameters())
        s.append('line')
        s.append('teacher')
        # s.append('state')
        # s.add('user')
        return s

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        # dd.logger.info("20160223 %s", self)
        qs = super(Activities, self).get_request_queryset(ar, **kwargs)
        if isinstance(qs, list):
            return qs

        if self._course_area is not None:
            qs = qs.filter(line__course_area=self._course_area)

        pv = ar.param_values
        if pv.topic:
            qs = qs.filter(line__topic=pv.topic)

        flt = Q(enrolments_until__isnull=True)
        flt |= Q(enrolments_until__gte=dd.today())
        if pv.can_enroll == dd.YesNo.yes:
            qs = qs.filter(flt)
        elif pv.can_enroll == dd.YesNo.no:
            qs = qs.exclude(flt)
        qs = PeriodEvents.active.add_filter(qs, pv)

        qs = self.model.add_param_filter(
            qs, show_exposed=pv.show_exposed)
        
        # if pv.start_date:
        #     # dd.logger.info("20160512 start_date is %r", pv.start_date)
        #     qs = PeriodEvents.started.add_filter(qs, pv)
        #     # qs = qs.filter(start_date__gte=pv.start_date)
        # if pv.end_date:
        #     qs = PeriodEvents.ended.add_filter(qs, pv)
        #     # qs = qs.filter(end_date__lte=pv.end_date)
        # dd.logger.info("20160512 %s", qs.query)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Activities, self).get_title_tags(ar):
            yield t

        if ar.param_values.topic:
            yield str(ar.param_values.topic)
        # for n in self.simple_param_fields:
        #     v = ar.param_values.get(n)
        #     if v:
        #         yield str(v)


class Courses(Activities):
    # required_roles = dd.login_required(CoursesUser)
    _course_area = CourseAreas.default
    required_roles = dd.login_required(CoursesUser)

    # courses_by_line = dd.ShowSlaveTable('courses.CoursesByLine')


class AllActivities(Activities):
    _course_area = None
    required_roles = dd.login_required(Explorer)
    column_names = "line:20 start_date:8 teacher user " \
                   "weekdays_text:10 times_text:10 *"


class CoursesByTeacher(Activities):
    master_key = "teacher"
    column_names = "start_date start_time end_time line room *"
    order_by = ['-start_date']


class MyCourses(My, Activities):
    column_names = "start_date:8 room name line workflow_buttons *"
    order_by = ['start_date']
    
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyCourses, self).param_defaults(ar, **kw)
        # kw.update(state=CourseStates.active)
        kw.update(show_exposed=dd.YesNo.yes)
        return kw


class MyCoursesGiven(Activities):
    label = _("My courses given")
    required_roles = dd.login_required(CoursesTeacher)
    column_names = "start_date detail_link weekdays_text times_text room workflow_buttons *"
    order_by = ['start_date', 'start_time']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyCoursesGiven, self).param_defaults(ar, **kw)
        kw.update(show_exposed=dd.YesNo.yes)
        u = ar.get_user()
        if isinstance(u, teacher_model):
            pass
        elif u.partner is not None:
            u = get_child(u.partner, teacher_model)
        kw['teacher'] = u
        return kw

    # @classmethod
    # def setup_request(self, ar):
    #     u = ar.get_user()
    #     if isinstance(u, teacher_model):
    #         ar.master_instance = u
    #     elif u.partner is not None:
    #         ar.master_instance = get_child(u.partner, teacher_model)
    #     super(MyCoursesGiven, self).setup_request(ar)
    

class CoursesByLine(Activities):
    master_key = "line"
    column_names = "detail_link weekdays_text room times_text teacher *"
    order_by = ['room__name', '-start_date']
    


class CoursesByTopic(Activities):
    master_key = 'line__topic'
    # master = 'courses.Topic'
    order_by = ['-start_date']
    column_names = "detail_link weekdays_text:10 times_text:10 "\
                   "max_places:8 confirmed "\
                   "free_places requested trying *"
    # column_names = "start_date:8 line:20 room:10 " \
    #                "weekdays_text:10 times_text:10"
    
    params_layout = """line teacher user state can_enroll:10"""

    allow_create = False  # because we cannot set a line for a new
                          # activity.

    # @classmethod
    # def get_filter_kw(self, ar, **kw):
    #     kw.update(line__topic=ar.master_instance)
    #     return kw

    # @classmethod
    # def get_request_queryset(self, ar):
    #     Course = rt.models.courses.Course
    #     topic = ar.master_instance
    #     if topic is None:
    #         return Course.objects.none()
    #     return Course.objects.filter(line__topic=topic)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(CoursesByTopic, self).param_defaults(ar, **kw)
        kw.update(show_exposed=dd.YesNo.yes)
        return kw


class CoursesBySlot(Activities):
    master_key = "slot"


class DraftCourses(Activities):
    label = _("Draft activities")
    column_names = 'detail_link room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(DraftCourses, self).param_defaults(ar, **kw)
        kw.update(state=CourseStates.draft)
        kw.update(user=ar.get_user())
        # kw.update(can_enroll=dd.YesNo.yes)
        return kw


class ActiveCourses(Activities):

    label = _("Current activities")
    column_names = 'detail_link enrolments:8 free_places teacher room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(ActiveCourses, self).param_defaults(ar, **kw)
        kw.update(state=CourseStates.active)
        kw.update(can_enroll=dd.YesNo.yes)
        return kw


class InactiveCourses(Activities):

    label = _("Inactive courses")
    column_names = 'detail_link enrolments:8 free_places room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(InactiveCourses, self).param_defaults(ar, **kw)
        kw.update(state=CourseStates.inactive)
        return kw


class ClosedCourses(Activities):

    label = _("Closed courses")
    column_names = 'detail_link enrolments:8 room *'
    hide_sums = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(ClosedCourses, self).param_defaults(ar, **kw)
        kw.update(state=CourseStates.closed)
        return kw

class EnrolmentDetail(dd.DetailLayout):
    main = """
    request_date user start_date end_date
    course pupil
    remark workflow_buttons
    confirmation_details
    """


class Enrolments(dd.Table):

    _course_area = None

    required_roles = dd.login_required((CoursesUser, CoursesTeacher))
    # debug_permissions=20130531
    model = 'courses.Enrolment'
    stay_in_grid = True
    parameters = mixins.ObservedDateRange(
        author=dd.ForeignKey(
            settings.SITE.user_model, blank=True, null=True),
        state=EnrolmentStates.field(blank=True, null=True),
        course_state=CourseStates.field(
            _("Course state"), blank=True, null=True),
        participants_only=models.BooleanField(
            _("Participants only"),
            help_text=_(
                "Hide cancelled enrolments. "
                "Ignored if you specify an explicit enrolment state."),
            default=True),
    )
    params_layout = """start_date end_date author state \
    course_state participants_only"""
    order_by = ['request_date']
    column_names = 'request_date course course__state pupil workflow_buttons user *'
    # hidden_columns = 'id state'
    insert_layout = """
    request_date user
    course pupil
    remark
    """
    detail_layout = "courses.EnrolmentDetail"

    @classmethod
    def get_known_values(self):
        if self._course_area is not None:
            return dict(course_area=self._course_area)
        return dict()

    @classmethod
    def create_instance(self, ar, **kw):
        if self._course_area is not None:
            kw.update(course_area=self._course_area)
        # dd.logger.info("20160714 %s", kw)
        return super(Enrolments, self).create_instance(ar, **kw)

    @classmethod
    def get_actor_label(self):
        if self._course_area is not None:
            return self._course_area.text
        return super(Enrolments, self).get_actor_label()

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Enrolments, self).get_request_queryset(ar, **kwargs)
        if isinstance(qs, list):
            return qs
        pv = ar.param_values
        if pv.author is not None:
            qs = qs.filter(user=pv.author)

        if pv.state:
            qs = qs.filter(state=pv.state)
        else:
            if pv.participants_only:
                qs = qs.exclude(state=EnrolmentStates.cancelled)

        if pv.course_state:
            qs = qs.filter(course__state=pv.course_state)

        if pv.start_date or pv.end_date:
            qs = PeriodEvents.active.add_filter(qs, pv)

        # if pv.start_date is None or pv.end_date is None:
        #     period = None
        # else:
        #     period = (pv.start_date, pv.end_date)
        # if period is not None:
        #     qs = qs.filter(dd.inrange_filter('request_date', period))

        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Enrolments, self).get_title_tags(ar):
            yield t

        if ar.param_values.state:
            yield str(ar.param_values.state)
        elif not ar.param_values.participants_only:
            yield str(_("Also ")) + str(EnrolmentStates.cancelled.text)
        if ar.param_values.course_state:
            yield str(
                settings.SITE.models.courses.Course._meta.verbose_name) \
                + ' ' + str(ar.param_values.course_state)
        if ar.param_values.author:
            yield str(ar.param_values.author)


class AllEnrolments(Enrolments):
    required_roles = dd.login_required(Explorer)
    order_by = ['-id']
    column_names = 'id request_date start_date end_date user course pupil pupil__birth_date pupil__age pupil__country pupil__city pupil__gender *'


class ConfirmAllEnrolments(dd.Action):
    label = _("Confirm all")
    select_rows = False
    http_method = 'POST'

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        assert obj is None

        def ok(ar):
            for obj in ar:
                obj.state = EnrolmentStates.confirmed
                obj.save()
                ar.set_response(refresh_all=True)

        msg = _(
            "This will confirm all %d enrolments in this list.") % ar.get_total_count()
        ar.confirm(ok, msg, _("Are you sure?"))


class PendingRequestedEnrolments(Enrolments):
    label = _("Pending requested enrolments")
    required_roles = dd.login_required(dd.SiteStaff)
    auto_fit_column_widths = True
    params_panel_hidden = True
    column_names = 'request_date course pupil remark user workflow_buttons'
    hidden_columns = 'id state'

    # confirm_all = ConfirmAllEnrolments()

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(PendingRequestedEnrolments, self).param_defaults(ar, **kw)
        kw.update(state=EnrolmentStates.requested)
        return kw


class PendingConfirmedEnrolments(Enrolments):
    label = _("Pending confirmed enrolments")
    required_roles = dd.login_required(dd.SiteStaff)
    auto_fit_column_widths = True
    params_panel_hidden = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(PendingConfirmedEnrolments, self).param_defaults(ar, **kw)
        kw.update(state=EnrolmentStates.confirmed)
        # kw.update(course_state=CourseStates.ended)
        return kw


class EnrolmentsByPupil(Enrolments):
    params_panel_hidden = True
    required_roles = dd.login_required(CoursesUser)
    master_key = "pupil"
    column_names = 'request_date course user:10 remark workflow_buttons *'
    auto_fit_column_widths = True

    insert_layout = """
    # course_area
    course
    # places option
    remark
    request_date user
    """

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(EnrolmentsByPupil, self).param_defaults(ar, **kw)
        kw.update(participants_only=False)
        return kw

    @classmethod
    def get_actor_label(cls):
        if cls._course_area is not None:
            courses = cls._course_area.text
        else:
            courses = rt.models.courses.Course._meta.verbose_name_plural
        return format_lazy(
            _("{enrolments} in {courses}"),
            enrolments=rt.models.courses.Enrolment._meta.verbose_name_plural,
            courses=courses)

class EnrolmentsByCourse(Enrolments):
    params_panel_hidden = True
    required_roles = dd.login_required((CoursesUser, CoursesTeacher))
    # required_roles = dd.login_required(CoursesUser)
    master_key = "course"
    column_names = 'request_date pupil places option ' \
                   'remark workflow_buttons *'
    auto_fit_column_widths = True
    # cell_edit = False
    display_mode = 'html'

    insert_layout = """
    pupil
    remark
    request_date user
    """

    label = _("Participants")

    # @classmethod
    # def get_actor_label(self):
    #     return rt.models.courses.Enrolment._meta.verbose_name_plural

class EnrolmentsByOption(Enrolments):
    label = _("Enrolments using this option")
    master_key = 'option'
    column_names = 'course pupil remark request_date *'
    order_by = ['request_date']
    

# class EntriesByCourse(cal.Events):
#     required = dd.login_required(user_groups='office')
#     master_key = 'course'
#     column_names = 'when_text:20 when_html summary workflow_buttons *'
#     auto_fit_column_widths = True


# dd.inject_field(
#     'cal.Event',
#     'course',
#     dd.ForeignKey(
#         'courses.Course',
#         blank=True, null=True,
#         help_text=_("Fill in only if this event is a session of a course."),
#         related_name="events_by_course"))





class StatusReport(Report):
    """Gives an overview about what's up today .

    """

    label = _("Status Report")
    required_roles = dd.login_required(CoursesUser)

    @classmethod
    def get_story(cls, self, ar):
        for topic in rt.models.courses.Topic.objects.all():
            sar = ar.spawn(
                rt.models.courses.CoursesByTopic, master_instance=topic)
            if sar.get_total_count():
                yield E.h3(str(topic))
                yield sar


