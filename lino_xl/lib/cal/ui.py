# -*- coding: UTF-8 -*-
# Copyright 2011-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import print_function, unicode_literals
from builtins import str
from collections import OrderedDict

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _, gettext
from lino import mixins
from lino.core.roles import Explorer
from lino.core.fields import TableRow
from lino.core import fields
from lino.utils.format_date import monthname
from lino.utils.format_date import day_and_month, day_and_weekday
from lino.modlib.users.mixins import My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator

from lino.utils import join_elems
from etgen.html import E, forcetext

from .choicelists import TaskStates
from .choicelists import GuestStates
from .choicelists import EntryStates
from .choicelists import AccessClasses
from .choicelists import PlannerColumns,Weekdays
from .choicelists import DurationUnits, YearMonths
from .choicelists import EventEvents

from .mixins import daterange_text
from .utils import when_text

from .roles import CalendarReader, GuestOperator

from calendar import Calendar as PythonCalendar
from datetime import timedelta, datetime

CALENDAR = PythonCalendar()


def date2pk(date):
    delta = date - dd.today()
    return delta.days


class RemoteCalendars(dd.Table):
    model = 'cal.RemoteCalendar'
    required_roles = dd.login_required(OfficeStaff)


class RoomDetail(dd.DetailLayout):
    main = """
    id name
    company contact_person display_color
    description
    cal.EntriesByRoom
    """


class Rooms(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    # required_roles = dd.login_required((OfficeStaff, CalendarReader))
    
    model = 'cal.Room'
    detail_layout = "cal.RoomDetail"
    insert_layout = """
    id name display_color
    company
    contact_person
    """

    detail_html_template = "cal/Room/detail.html"

class AllRooms(Rooms):    
    required_roles = dd.login_required(OfficeStaff)


# class Priorities(dd.Table):
#     required_roles = dd.login_required(OfficeStaff)
#     model = 'cal.Priority'
#     column_names = 'name *'
#

class Calendars(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.Calendar'

    insert_layout = """
    name
    color
    """
    detail_layout = """
    name color id
    description SubscriptionsByCalendar
    """


class Subscriptions(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.Subscription'
    order_by = ['calendar__name']
    # insert_layout = """
    # label
    # event_type
    # """
    # detail_layout = """
    # label user color
    # event_type team other_user room
    # description
    # """

# class MySubscriptions(Subscriptions, ByUser):
    # pass

# class SubscriptionsByCalendar(Subscriptions):
    # master_key = 'calendar'


class SubscriptionsByUser(Subscriptions):
    required_roles = dd.login_required(OfficeUser)
    master_key = 'user'
    auto_fit_column_widths = True


class SubscriptionsByCalendar(Subscriptions):
    required_roles = dd.login_required(OfficeUser)
    master_key = 'calendar'
    auto_fit_column_widths = True


def check_subscription(user, calendar):
    # Check whether the given subscription exists. If not, create it.
    Subscription = rt.models.cal.Subscription
    if calendar is None:
        return
    try:
        Subscription.objects.get(user=user, calendar=calendar)
    except Subscription.DoesNotExist:
        sub = Subscription(user=user, calendar=calendar)
        sub.full_clean()
        sub.save()


class UserDetailMixin(dd.DetailLayout):

    cal_left = """
    event_type access_class
    calendar
    cal.SubscriptionsByUser
    # cal.MembershipsByUser
    """

    cal = dd.Panel(
        """
        cal_left:30 cal.TasksByUser:60
        """,
        label=dd.plugins.cal.verbose_name,
        required_roles=dd.login_required(OfficeUser))

    
class Tasks(dd.Table):
    model = 'cal.Task'
    required_roles = dd.login_required(OfficeStaff)
    stay_in_grid = True
    column_names = 'priority start_date summary workflow_buttons *'
    order_by = ["priority", "-start_date", "-start_time"]

    detail_layout = """
    start_date priority due_date id workflow_buttons
    summary
    user project
    #event_type owner created:20 modified:20
    description #notes.NotesByTask
    """

    insert_layout = dd.InsertLayout("""
    summary
    user project
    """, window_size=(50, 'auto'))

    params_panel_hidden = True

    parameters = mixins.ObservedDateRange(
        user=dd.ForeignKey(settings.SITE.user_model,
                           verbose_name=_("Managed by"),
                           blank=True, null=True,
                           help_text=_("Only rows managed by this user.")),
        project=dd.ForeignKey(settings.SITE.project_model,
                              blank=True, null=True),
        state=TaskStates.field(blank=True,
                               help_text=_("Only rows having this state.")),
    )

    params_layout = """
    start_date end_date user state project
    """

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        # logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Tasks, self).get_request_queryset(ar, **kwargs)

        if ar.param_values.user:
            qs = qs.filter(user=ar.param_values.user)

        if settings.SITE.project_model is not None and ar.param_values.project:
            qs = qs.filter(project=ar.param_values.project)

        if ar.param_values.state:
            qs = qs.filter(state=ar.param_values.state)

        if ar.param_values.start_date:
            qs = qs.filter(start_date__gte=ar.param_values.start_date)
        if ar.param_values.end_date:
            qs = qs.filter(start_date__lte=ar.param_values.end_date)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Tasks, self).get_title_tags(ar):
            yield t
        if ar.param_values.start_date or ar.param_values.end_date:
            yield str(_("Dates %(min)s to %(max)s") % dict(
                min=ar.param_values.start_date or'...',
                max=ar.param_values.end_date or '...'))

        if ar.param_values.state:
            yield str(ar.param_values.state)

        # if ar.param_values.user:
        #     yield str(ar.param_values.user)

        if settings.SITE.project_model is not None and ar.param_values.project:
            yield str(ar.param_values.project)

    @classmethod
    def apply_cell_format(self, ar, row, col, recno, td):
        """
        Enhance today by making background color a bit darker.
        """
        if row.start_date == settings.SITE.today():
            td.set('bgcolor', "gold")


class TasksByController(Tasks):
    master_key = 'owner'
    required_roles = dd.login_required(OfficeUser)
    column_names = 'priority start_date summary workflow_buttons id'
    # hidden_columns = set('owner_id owner_type'.split())
    auto_fit_column_widths = True


class TasksByUser(Tasks):
    master_key = 'user'
    required_roles = dd.login_required(OfficeUser)


class MyTasks(Tasks):
    label = _("My tasks")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'priority start_date summary workflow_buttons project'
    params_panel_hidden = True
    default_end_date_offset = 30
    """Number of days to go into the future. The default value for
    :attr:`end_date` will be :meth:`today
    <lino.core.site.Site.today>` + that number of days.

    """

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyTasks, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        kw.update(state=TaskStates.todo)
        # kw.update(start_date=settings.SITE.today())
        kw.update(end_date=settings.SITE.today(
            self.default_end_date_offset))
        return kw


#if settings.SITE.project_model:

class TasksByProject(Tasks):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    master_key = 'project'
    column_names = 'priority start_date user summary owner workflow_buttons *'


class GuestRoles(dd.Table):
    model = 'cal.GuestRole'
    required_roles = dd.login_required(dd.SiteStaff, OfficeUser)
    order_by = ['ref', 'name', 'id']
    column_names = "ref name id *"
    detail_layout = """
    ref name id
    cal.GuestsByRole
    """

class GuestDetail(dd.DetailLayout):
    window_size = (60, 'auto')
    main = """
    event partner role
    state workflow_buttons
    remark 
    # outbox.MailsByController
    """

class Guests(dd.Table):
    model = 'cal.Guest'
    # required_roles = dd.login_required((OfficeUser, OfficeOperator))
    required_roles = dd.login_required(GuestOperator)
    column_names = 'partner role workflow_buttons remark event *'
    order_by = ['-event__start_date', '-event__start_time']
    stay_in_grid = True
    detail_layout = "cal.GuestDetail"
    insert_layout = dd.InsertLayout("""
    event
    partner
    role
    """, window_size=(60, 'auto'))

    parameters = mixins.ObservedDateRange(
        user=dd.ForeignKey(settings.SITE.user_model,
                           verbose_name=_("Responsible user"),
                           blank=True, null=True,
                           help_text=_("Only rows managed by this user.")),
        project=dd.ForeignKey(settings.SITE.project_model,
                              blank=True, null=True),
        partner=dd.ForeignKey(dd.plugins.cal.partner_model,
                              blank=True, null=True),

        event_state=EntryStates.field(
            blank=True,
            verbose_name=_("Event state"),
            help_text=_("Only rows on calendar entries having this state.")),
        guest_state=GuestStates.field(
            blank=True,
            verbose_name=_("Guest state"),
            help_text=_("Only rows having this guest state.")),
    )

    params_layout = """start_date end_date user event_state guest_state
    project partner"""

    @classmethod
    def get_table_summary(cls, obj, ar):
        return get_calendar_summary(cls, obj, ar)
    
    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Guests, self).get_request_queryset(ar, **kwargs)

        if isinstance(qs, list):
            return qs
        pv = ar.param_values
        if pv.user:
            qs = qs.filter(event__user=pv.user)
        if settings.SITE.project_model is not None and pv.project:
            qs = qs.filter(event__project=pv.project)

        if pv.event_state:
            qs = qs.filter(event__state=pv.event_state)

        if pv.guest_state:
            qs = qs.filter(state=pv.guest_state)

        if pv.partner:
            qs = qs.filter(partner=pv.partner)

        # we test whether the *start_date* of event is within the
        # given range. Filtering guests by the end_date of their event
        # is currently not supported.
        if pv.start_date:
            qs = qs.filter(event__start_date__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(event__start_date__lte=pv.end_date)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Guests, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.start_date or pv.end_date:
            yield str(_("Dates %(min)s to %(max)s") % dict(
                min=pv.start_date or'...',
                max=pv.end_date or '...'))

        if pv.event_state:
            yield str(pv.event_state)

        if pv.partner:
            yield str(pv.partner)

        if pv.guest_state:
            yield str(pv.guest_state)

        # if pv.user:
        #     yield str(pv.user)

        if settings.SITE.project_model is not None and pv.project:
            yield str(pv.project)

class AllGuests(Guests):
    required_roles = dd.login_required(GuestOperator, Explorer)

class GuestsByEvent(Guests):
    master_key = 'event'
    required_roles = dd.login_required(GuestOperator)
    # required_roles = dd.login_required(OfficeUser)
    auto_fit_column_widths = True
    column_names = 'partner role workflow_buttons remark *'
    order_by = ['partner__name', 'partner__id']


class GuestsByRole(Guests):
    master_key = 'role'
    required_roles = dd.login_required(GuestOperator)
    # required_roles = dd.login_required(OfficeUser)


class GuestsByPartner(Guests):
    label = _("Presences")
    master_key = 'partner'
    required_roles = dd.login_required(GuestOperator)
    # required_roles = dd.login_required(OfficeUser)
    column_names = 'event__when_text event_summary event__user role workflow_buttons *'
    auto_fit_column_widths = True
    display_mode = "summary"
    order_by = ['-event__start_date', '-event__start_time']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(GuestsByPartner, self).param_defaults(ar, **kw)
        # kw.update(event_state=EntryStates.took_place)
        kw.update(end_date=dd.today(7))
        return kw


class MyPresences(Guests):
    required_roles = dd.login_required(OfficeUser)
    order_by = ['-event__start_date', '-event__start_time']
    label = _("My presences")
    column_names = 'event__start_date event__start_time event_summary role workflow_buttons remark *'
    params_panel_hidden = True

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        # logger.info("20130809 MyPresences")
        if ar.get_user().partner is None:
            raise Warning("Action not available for users without partner")
        return super(MyPresences, self).get_request_queryset(ar, **kwargs)

    @classmethod
    def get_row_permission(cls, obj, ar, state, ba):
        if ar.get_user().partner is None:
            return False
        return super(MyPresences, cls).get_row_permission(
            obj, ar, state, ba)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyPresences, self).param_defaults(ar, **kw)
        u = ar.get_user()
        if u is not None:
            kw.update(partner=u.partner)
        # kw.update(guest_state=GuestStates.invited)
        # kw.update(start_date=settings.SITE.today())
        return kw

    # @classmethod
    # def get_request_queryset(self,ar):
        # ar.master_instance = ar.get_user().partner
        # return super(MyPresences,self).get_request_queryset(ar)

# class MyPendingInvitations(Guests):
class MyPendingPresences(MyPresences):
    label = _("My pending invitations")
    # filter = models.Q(state=GuestStates.invited)
    column_names = 'event__when_text role workflow_buttons remark'
    params_panel_hidden = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyPendingPresences, self).param_defaults(ar, **kw)
        # kw.update(partner=ar.get_user().partner)
        # kw.update(user=None)
        kw.update(guest_state=GuestStates.invited)
        kw.update(start_date=settings.SITE.today())
        return kw

class MyGuests(Guests):
    label = _("My guests")
    required_roles = dd.login_required(OfficeUser)
    order_by = ['-event__start_date', '-event__start_time']
    column_names = ("event__start_date event__start_time "
                    "event_summary role workflow_buttons remark *")

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyGuests, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        kw.update(guest_state=GuestStates.invited)
        kw.update(start_date=settings.SITE.today())
        return kw


class EventTypes(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.EventType'
    order_by = ['ref', 'name', 'id']
    column_names = "ref name planner_column is_appointment force_guest_states all_rooms *"

    detail_layout = """
    ref id planner_column default_duration 
    name 
    event_label
    # description
    #build_method #template start_date max_days max_conflicting email_template attach_to_email
    is_appointment force_guest_states fill_presences all_rooms locks_user transparent
    EntriesByType
    """

    insert_layout = dd.InsertLayout("""
    name ref
    event_label
    """, window_size=(60, 'auto'))


class RecurrentEvents(dd.Table):
    model = 'cal.RecurrentEvent'
    required_roles = dd.login_required(OfficeStaff)
    column_names = "start_date end_date name every_unit event_type *"
    auto_fit_column_widths = True
    order_by = ['start_date']

    insert_layout = """
    name
    start_date end_date every_unit event_type
    """
    insert_layout_width = 80

    detail_layout = """
    name
    id user event_type
    start_date start_time  end_date end_time
    every_unit every max_events
    monday tuesday wednesday thursday friday saturday sunday
    description cal.EntriesByController
    """


# ~ from lino_xl.lib.workflows import models as workflows # Workflowable

# class Components(dd.Table):
# ~ # class Components(dd.Table,workflows.Workflowable):

    # workflow_owner_field = 'user'
    # workflow_state_field = 'state'

    # def disable_editing(self,request):
    # def get_row_permission(cls,row,user,action):
        # if row.rset: return False

    # @classmethod
    # def get_row_permission(cls,action,user,row):
        # if not action.readonly:
            # if row.user != user and user.level < UserLevel.manager:
                # return False
        # if not super(Components,cls).get_row_permission(action,user,row):
            # return False
        # return True


class EventDetail(dd.DetailLayout):
    start = "start_date start_time"
    end = "end_date end_time"
    main = """
    event_type summary user
    start end #all_day assigned_to #duration #state
    room project owner workflow_buttons
    # owner created:20 modified:20
    description GuestsByEvent #outbox.MailsByController
    """

class EventInsert(dd.InsertLayout):
    main = """
    start_date start_time end_date end_time
    summary
    # room priority access_class transparent
    """


class Events(dd.Table):

    model = 'cal.Event'
    required_roles = dd.login_required(OfficeStaff)
    column_names = 'when_text:20 user summary event_type id *'

    # hidden_columns = """
    # priority access_class transparent
    # owner created modified
    # description
    # sequence auto_type build_time owner owner_id owner_type
    # end_date end_time
    # """

    order_by = ["start_date", "start_time", "id"]

    detail_layout = 'cal.EventDetail'
    insert_layout = 'cal.EventInsert'
    detail_html_template = "cal/Event/detail.html"

    params_panel_hidden = True
  # ~ next = NextDateAction() # doesn't yet work. 20121203

    # fixed_states = set(EntryStates.filter(fixed=True))
    # pending_states = set([es for es in EntryStates if not es.fixed])
    # pending_states = set(EntryStates.filter(fixed=False))

    params_layout = "user event_type room project presence_guest"

    # 20190620
    # @classmethod
    # def setup_parameters(cls, params):
    #     cls.params_layout = rt.models.cal.Event.params_layout
    #     params = rt.models.cal.Event.setup_parameters(params)
    #     return super(Events, cls).setup_parameters(params)


    @classmethod
    def get_table_summary(cls, obj, ar):
        # print("20181121 get_table_summary", cls)
        return get_calendar_summary(cls, obj, ar)
    
    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        # print("20181121a get_request_queryset", self)
        qs = super(Events, self).get_request_queryset(ar, **kwargs)
        pv = ar.param_values
        return rt.models.cal.Event.calendar_param_filter(qs, pv)


    @classmethod
    def get_title_tags(self, ar):
        for t in super(Events, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.start_date or pv.end_date:
            yield daterange_text(
                pv.start_date,
                pv.end_date)

        if pv.state:
            yield str(pv.state)

        if pv.event_type:
            yield str(pv.event_type)

        # if pv.user:
        #     yield str(pv.user)

        if pv.room:
            yield str(pv.room)

        if settings.SITE.project_model is not None and pv.project:
            yield str(pv.project)

        if pv.assigned_to:
            yield str(self.parameters['assigned_to'].verbose_name) \
                + ' ' + str(pv.assigned_to)

    @classmethod
    def apply_cell_format(self, ar, row, col, recno, td):
        """
        Enhance today by making background color a bit darker.
        """
        if row.start_date == settings.SITE.today():
            td.set('bgcolor', "#bbbbbb")

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(Events, self).param_defaults(ar, **kw)
        kw.update(start_date=settings.SITE.site_config.hide_events_before)
        return kw

    
class AllEntries(Events):
    required_roles = dd.login_required(Explorer)
    params_layout = """
    start_date end_date observed_event state
    user assigned_to project event_type room show_appointments
    """

class EntriesByType(Events):
    master_key = 'event_type'


class ConflictingEvents(Events):
    label = ' ⚔ '  # 2694
    help_text = _("Show events conflicting with this one.")

    master = 'cal.Event'
    column_names = 'start_date start_time end_time project room user *'

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = ar.master_instance.get_conflicting_events()
        if qs is None:
            return rt.models.cal.Event.objects.none()
        return qs
    

class PublicEntries(Events):
    required_roles = dd.login_required(CalendarReader)
    
    column_names = 'detail_link room event_type  *'
    filter = models.Q(access_class=AccessClasses.public)
    
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(PublicEntries, self).param_defaults(ar, **kw)
        # kw.update(show_appointments=dd.YesNo.yes)
        kw.update(start_date=settings.SITE.today())
        # kw.update(end_date=settings.SITE.today())
        return kw



class EntriesByDay(Events):
    required_roles = dd.login_required((OfficeOperator, OfficeUser))
    label = _("Appointments today")
    column_names = 'start_time end_time duration room event_type summary owner workflow_buttons *'
    auto_fit_column_widths = True
    params_panel_hidden = False

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(EntriesByDay, self).param_defaults(ar, **kw)
        kw.update(show_appointments=dd.YesNo.yes)
        kw.update(start_date=settings.SITE.today())
        kw.update(end_date=settings.SITE.today())
        return kw

    @classmethod
    def create_instance(self, ar, **kw):
        kw.update(start_date=ar.param_values.start_date)
        return super(EntriesByDay, self).create_instance(ar, **kw)

    @classmethod
    def get_title_base(self, ar):
        return when_text(ar.param_values.start_date)

    @classmethod
    def as_link(cls, ar, today, txt=None):
        if ar is None:
            return ''
        if today is None:
            today = settings.SITE.today()
        if txt is None:
            txt = when_text(today)
        pv = dict(start_date=today)
        # TODO: what to do with events that span multiple days?
        pv.update(end_date=today)
        target = ar.spawn(cls, param_values=pv)
        return ar.href_to_request(target, txt)


# class EntriesByType(Events):
    # master_key = 'type'

# class EntriesByPartner(Events):
    # required = dd.login_required(user_groups='office')
    # master_key = 'user'


class EntriesByRoom(Events):

    """
    """
    master_key = 'room'


# from etgen.html import Table, tostring

class Year(object):
    def __init__(self, year):
        self.year = year
        self.months = [[] for i in range(12)]

PLAIN_MODE = 0
UL_MODE = 1
TABLE_MODE = 2

class CalendarRenderer(object):
    def __init__(self, model):
        self.years = OrderedDict()
        self.mode = PLAIN_MODE
        self.model = model

    def collect(self, obj):
        if self.model is rt.models.cal.Guest:
            d = obj.event.start_date
        else:
            d = obj.start_date
        
        if d.year in self.years:
            y = self.years[d.year]
        else:
            y = Year(d.year)
            self.years[d.year] = y
        y.months[d.month-1].append(obj)

    def analyze_view(self, max_months=6):
        count1 = count2 = 0
        nyears = 0
        for y in self.years.values():
            nmonths = 0
            for m in y.months:
                if len(m):
                    nmonths += 1
                    count1 += 1
                    if len(m) > 1:
                        count2 += 1
            if nmonths:
                nyears += 1
                        
        if count1 <= max_months:
            self.mode = UL_MODE
        elif count2:
            # self.mode = TABLE_MODE
            self.mode = UL_MODE
        else:
            self.mode = PLAIN_MODE

    def to_html(self, ar):
        self.analyze_view()
        
        if self.mode == TABLE_MODE:
            sep = ' '
            fmt = day_and_weekday
        elif self.mode == UL_MODE:
            sep = ' '
            fmt = day_and_weekday
        elif self.mode == PLAIN_MODE:
            sep = ', '
            fmt = dd.fds

        def rnd(obj, ar):
            if self.model is rt.models.cal.Guest:
                d = obj.event.start_date
                evt = obj.event
            else:
                d = obj.start_date
                evt = obj
            # if show_auto_num and evt.auto_type:
            #     yield str(evt.auto_type)+":"
            yield ar.obj2html(evt, fmt(d))
            if obj.state.button_text:
                yield str(obj.state.button_text)
            # return (fdmy(d) + ": ", ar.obj2html(evt, lbl))

        
            
        def xxx(list_of_entries):
            elems = []
            # for e in reversed(list_of_entries):
            for e in list_of_entries:
                if len(elems):
                    elems.append(sep)
                elems.extend(rnd(e, ar))
            return elems
        
        if self.mode == TABLE_MODE:
            rows = []
            cells = [E.th("")] + [E.th(monthname(m+1)) for m in range(12)]
            # print(''.join([tostring(c) for c in cells]))
            rows.append(E.tr(*cells))
            for y in self.years.values():
                cells = [E.td(str(y.year), width="4%")]
                for m in y.months:
                    # every m is a list of etree elems
                    cells.append(E.td(*xxx(m), width="8%", **ar.renderer.cellattrs))
                # print(str(y.year) +":" + ''.join([tostring(c) for c in cells]))
                rows.append(E.tr(*cells))
            return E.table(*rows, **ar.renderer.tableattrs)
        
        if self.mode == UL_MODE:
            items = []
            for y in self.years.values():
                for m, lst in enumerate(reversed(y.months)):
                    # January is [11], Dec is [0]
                    if len(lst):
                        items.append(E.li(
                            monthname(12-m), " ", str(y.year), ": ", *xxx(lst)))
            return E.ul(*items)
        
        if self.mode == PLAIN_MODE:
            elems = []
            for y in self.years.values():
                for lst in y.months:
                    if len(lst):
                        if len(elems):
                            elems.append(sep)
                        elems.extend(xxx(lst))
            return E.p(*elems)
        
        raise Exception("20180720")
        
        
def get_calendar_summary(cls, obj, ar):
    # print("20181121 get_calendar_summary", cls)
    # note that objects can be either Event or Guest. if the view
    # is called for Guest, we waht to display the guest states
    # (not the event states). But when user clicks on a date they
    # want to show the event even when we are calling from Guest.
    if ar is None or obj is None:
        return ''
    state_coll = {}
    cal = CalendarRenderer(cls.model)
    # sar = ar.spawn(parent=ar, master_instance=obj)
    # sar = ar.actor.request(parent=ar, master_instance=obj)
    sar = cls.request_from(ar, master_instance=obj)
    # sar = cls.request(parent=ar, master_instance=obj)
    # print("20181121 {}".format(ar.actor))
    # print("20181121 {}".format(cls.get_filter_kw(sar)))
    # print("20181121 {}".format(len(list(sar))))
    for obj in sar:
        if obj.state in state_coll:
            state_coll[obj.state] += 1
        else:
            state_coll[obj.state] = 1
        cal.collect(obj)

    elems = [cal.to_html(ar)]
    # choicelist = EntryStates
    choicelist = cls.workflow_state_field.choicelist
    ul = []
    for st in choicelist.get_list_items():
        ul.append(_("{} : {}").format(st, state_coll.get(st, 0)))
    toolbar = []
    toolbar += join_elems(ul, sep=', ')
    # elems = join_elems(ul, sep=E.br)
    if isinstance(obj, rt.models.cal.EventGenerator):
        ar1 = obj.do_update_events.request_from(sar)
        if ar1.get_permission():
            btn = ar1.ar2button(obj)
            toolbar.append(btn)

    ar2 = cls.insert_action.request_from(sar)
    if ar2.get_permission():
        btn = ar2.ar2button()
        toolbar.append(btn)

    if len(toolbar):
        toolbar = join_elems(toolbar, sep=' ')
        elems.append(E.p(*toolbar))

    return ar.html_text(E.div(*elems))
    


class EntriesByController(Events):
    required_roles = dd.login_required((OfficeOperator, OfficeUser))
    # required_roles = dd.login_required(OfficeUser)
    master_key = 'owner'
    column_names = 'when_text summary workflow_buttons auto_type user event_type *'
    # column_names = 'when_text:20 when_html summary workflow_buttons *'
    auto_fit_column_widths = True
    display_mode = "summary"
    order_by = ["-start_date", "-start_time", "auto_type", "id"]
    # order_by = ['seqno']

    

if settings.SITE.project_model:

    class EntriesByProject(Events):
        required_roles = dd.login_required((OfficeUser, OfficeOperator))
        master_key = 'project'
        auto_fit_column_widths = True
        stay_in_grid = True
        column_names = 'when_text user summary workflow_buttons *'
        # column_names = 'when_text user summary workflow_buttons'
        insert_layout = """
        start_date start_time end_time
        summary
        event_type
        """

    @classmethod
    def create_instance(cls, ar, **kw):
        mi = ar.master_instance
        if mi is not None:
            kw['project'] = mi
        return super(EntriesByProject, cls).create_instance(ar, **kw)



class EntriesByGuest(Events):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    master_key = 'guest__partner'
    auto_fit_column_widths = True
    stay_in_grid = True
    column_names = 'when_text user summary workflow_buttons'
    # column_names = 'when_text user summary workflow_buttons'
    insert_layout = """
    start_date start_time end_time
    summary
    event_type
    """
    display_mode = "summary"
    order_by = ['-start_date', '-start_time']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(EntriesByGuest, self).param_defaults(ar, **kw)
        # kw.update(event_state=EntryStates.took_place)
        kw.update(end_date=dd.today(7))
        return kw

    @classmethod
    def after_create_instance(cls, obj, ar):
        mi = ar.master_instance
        if mi is not None:
            Guest = rt.models.cal.Guest
            if not Guest.objects.filter(partner=mi, event=obj).exists():
                Guest.objects.create(partner=mi, event=obj)
        super(EntriesByGuest, cls).after_create_instance(obj, ar)


class OneEvent(Events):
    show_detail_navigator = False
    use_as_default_table = False
    required_roles = dd.login_required(
        (OfficeOperator, OfficeUser, CalendarReader))
    # required_roles = dd.login_required(OfficeUser)


class MyEntries(Events):
    label = _("My appointments")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'detail_link project #event_type #summary workflow_buttons *'
    auto_fit_column_widths = True
    params_layout = """
    start_date end_date observed_event state
    user assigned_to project event_type room show_appointments
    """

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyEntries, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        kw.update(show_appointments=dd.YesNo.yes)
        # kw.update(assigned_to=ar.get_user())
        # logger.info("20130807 %s %s",self,kw)
        kw.update(start_date=dd.today())
        # kw.update(end_date=settings.SITE.today(14))
        return kw

    @classmethod
    def create_instance(self, ar, **kw):
        kw.update(start_date=ar.param_values.start_date)
        return super(MyEntries, self).create_instance(ar, **kw)


class MyEntriesToday(MyEntries):
    label = _("My appointments today")
    column_names = 'start_time end_time project event_type '\
                   'summary workflow_buttons *'

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyEntriesToday, self).param_defaults(ar, **kw)
        kw.update(end_date=dd.today())
        return kw



class MyAssignedEvents(MyEntries):
    label = _("Appointments assigned to me")
    required_roles = dd.login_required(OfficeUser)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyAssignedEvents, self).param_defaults(ar, **kw)
        kw.update(user=None)
        kw.update(assigned_to=ar.get_user())
        return kw

    @classmethod
    def get_welcome_messages(cls, ar, **kw):
        sar = ar.spawn(cls)
        count = sar.get_total_count()
        if count > 0:
            txt = _("{} appointments have been assigned to you.").format(count)
            yield ar.href_to_request(sar, txt)


class OverdueAppointments(Events):
    required_roles = dd.login_required(OfficeStaff)
    label = _("Overdue appointments")
    column_names = 'when_text user project owner event_type summary workflow_buttons *'
    auto_fit_column_widths = True
    params_panel_hidden = False

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(OverdueAppointments, self).param_defaults(ar, **kw)
        kw.update(observed_event=EventEvents.pending)
        kw.update(end_date=settings.SITE.today(-1))
        kw.update(show_appointments=dd.YesNo.yes)
        return kw

class MyOverdueAppointments(My, OverdueAppointments):
    label = _("My overdue appointments")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'detail_link owner event_type workflow_buttons *'

class MyUnconfirmedAppointments(MyEntries):
    required_roles = dd.login_required(OfficeUser)
    label = _("My unconfirmed appointments")
    column_names = 'when_html project summary workflow_buttons *'
    auto_fit_column_widths = True
    params_panel_hidden = False
    filter = models.Q(state__in=(EntryStates.suggested, EntryStates.draft))

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyUnconfirmedAppointments, self).param_defaults(ar, **kw)
        # kw.update(observed_event=EventEvents.pending)
        # kw.update(state=EntryStates.draft)
        kw.update(start_date=settings.SITE.today(-14))
        kw.update(end_date=settings.SITE.today(14))
        # kw.update(show_appointments=dd.YesNo.yes)
        return kw



class EventPolicies(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.EventPolicy'
    column_names = 'name  event_type max_events every every_unit monday tuesday wednesday thursday friday saturday sunday *'
    # detail_layout = """
    # id name
    # max_events every every_unit event_type
    # monday tuesday wednesday thursday friday saturday sunday
    # """


def weekname(date):
    return _("Week {1} / {0}").format(*date.isocalendar())


@dd.python_2_unicode_compatible
class Day(TableRow):

    def __init__(self, offset=0, ar=None, navigation_mode="day"):
        self.date = dd.today(offset)
        self.pk = offset
        self.ar = ar
        self.navigation_mode = navigation_mode

    def __str__(self):
        if self.navigation_mode == "day":
            return when_text(self.date)
        elif self.navigation_mode == "week":
            return weekname(self.date)
        else:
            return monthname(self.date.month) + " " + str(self.date.year)

    def skipmonth(self, n):
        return DurationUnits.months.add_duration(self.date, n)

class DayDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 cal.PlannerByDay:85"


def make_link_funcs(ar):
    sar_daily = ar.spawn(DailyView)
    sar_weekly = ar.spawn(WeeklyView)
    sar_monthly = ar.spawn(MonthlyView)
    sar_monthly.param_values = sar_weekly.param_values = sar_daily.param_values = ar.param_values
    rnd = settings.SITE.kernel.default_renderer

    def weekly(day, text):
        return rnd.ar2button(sar_weekly,day,text, style="", icon_name=None)

    def daily(day, text):
        return rnd.ar2button(sar_daily,day,text, style="", icon_name=None)

    def monthly(day, text):
        return rnd.ar2button(sar_monthly,day,text, style="", icon_name=None)

    return daily, weekly, monthly


class EventsParameters(object):

    @classmethod
    def class_init(cls):
        cls.params_layout = rt.models.cal.Events.params_layout
        super(EventsParameters, cls).class_init()

    @classmethod
    def setup_parameters(cls, params):
        return rt.models.cal.Event.setup_parameters(params)


class Days(dd.VirtualTable):
    # every row is a Day instance. Note that Day can be overridden.

    # required_roles = dd.login_required((OfficeUser, OfficeOperator))
    required_roles = dd.login_required(OfficeUser)
    column_names = "detail_link *"
    parameters = mixins.ObservedDateRange(
        user=dd.ForeignKey('users.User', null=True, blank=True))
    model = 'cal.Day'
    editable = False
    navigation_mode = "day"  # or "week" or "month"
    abstract = True

    @classmethod
    def get_navinfo(cls, ar, day):
        assert isinstance(day, Day)
        day.navigation_mode = ar.actor.navigation_mode  # so that str() gives the right formar
        ni = dict(recno=day.pk, message=str(day))

        if cls.navigation_mode == "month":
            ni.update(next=date2pk(day.skipmonth(1)))
            ni.update(prev=date2pk(day.skipmonth(-1)))
            ni.update(first=day.pk - 365)
            ni.update(last=day.pk + 365)
        elif cls.navigation_mode == "week":
            ni.update(next=day.pk + 7)
            ni.update(prev=day.pk - 7)
            ni.update(first=date2pk(day.skipmonth(-1)))
            ni.update(last=date2pk(day.skipmonth(1)))
        elif cls.navigation_mode == "day":
            ni.update(next=day.pk + 1)
            ni.update(prev=day.pk - 1)
            ni.update(first=date2pk(day.skipmonth(-1)))
            ni.update(last=date2pk(day.skipmonth(1)))
        else:
            raise Exception("Invalid navigation_mode {}".format(
                cls.navigation_mode))
        return ni

    @dd.virtualfield(models.IntegerField(_("Day number")))
    def day_number(cls, obj, ar):
        return obj.pk

    @classmethod
    def get_pk_field(cls):
        # return pk_field
        # return PK_FIELD
        # return cls.get_data_elem('day_number')
        return cls.day_number.return_type

    @classmethod
    def get_row_by_pk(cls, ar, pk):
        """
        pk is the offset from beginning_of_time
        """
        #if pk is None:
        #    pk = "0"
        # return dd.today(int(pk))
        # if ar is None:
        #     return cls.model(int(pk))
        # return cls.model(int(pk), ar.actor.navigation_mode)
        return cls.model(int(pk), ar, cls.navigation_mode)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        home = cls.get_row_by_pk(ar, 0)
        ni = cls.get_navinfo(ar, home)

        pv = ar.param_values
        date = pv.start_date or dd.today(ni['first'])
        last = pv.end_date or dd.today(ni['last'])
        if cls.navigation_mode == "day":
            step = lambda x: x + timedelta(days=1)
        elif cls.navigation_mode == "week":
            step = lambda x: x + timedelta(days=7)
        else:
            step = lambda x: DurationUnits.months.add_duration(x, 1)

        while date <= last:
            yield cls.get_row_by_pk(ar, date2pk(date))
            date = step(date)

        # # return []  # not needed for detail view
        # days = []
        # pv = ar.param_values
        # sd = pv.start_date or dd.today()
        # ed = pv.end_date or sd
        # if sd > ed:
        #     return []
        # # while sd <= ed:
        # #     days.append(sd)
        # #     sd = sd + relativedelta(days=1)
        #
        # if cls.reverse_sort_order:
        #     step = -1
        #     pk = date2pk(ed)
        # else:
        #     pk = date2pk(sd)
        #     step = 1
        # while True:  # sd <= ed:
        #     # print(20181229, sd)
        #     d = cls.model(pk, ar)
        #     if d.date > ed or d.date < sd:
        #         return days
        #     days.append(d)
        #     pk += step


class CalendarView(Days):

    """
    Base class for the three calendar views.

    We want all calendar view actors to inherit params_layout from the
    cal.Events table as defined by the application. But *after* the
    custom_layout_module has been loaded.  So we override the class_init()
    method.

    """

    # parameters = Calendarparameters
    # params_layout = Calendarparams_layout
    # reverse_sort_order = False
    abstract = True
    use_detail_param_panel = True
    params_panel_hidden = False
    display_mode = "html"
    # hide_top_toolbar = True
    detail_layout = 'cal.DayDetail'

    @classmethod
    def get_default_action(cls):
        return dd.ShowDetail(cls.detail_layout)

    @dd.htmlbox()
    def navigation_panel(cls, obj, ar):

        day_view = bool(cls.navigation_mode == 'day')
        weekly_view = bool(cls.navigation_mode == 'week')
        month_view = bool(cls.navigation_mode == 'month')

        # todo ensure that the end of the month is always in the view.
        today = obj.date
        daily, weekly, monthly = make_link_funcs(ar)
        long_unit = DurationUnits.years if month_view else DurationUnits.months
        prev_month = Day(date2pk(long_unit.add_duration(today, -1)))
        next_month = Day(date2pk(long_unit.add_duration(today, 1)))
        next_unit = DurationUnits.weeks if weekly_view else DurationUnits.days if day_view else DurationUnits.months
        prev_view = Day(date2pk(next_unit.add_duration(today, -1)))
        next_view = Day(date2pk(next_unit.add_duration(today, 1)))
        # current_view = weekly if weekly_view else daily
        current_view = daily
        if not day_view:
            current_view = monthly if month_view else weekly

        elems = [] #cls.calender_header(ar)

        # Month div
        rows, cells = [], []
        for i, month in enumerate(YearMonths.get_list_items()):
            # each week is a list of seven datetime.date objects.
            pk = date2pk(DurationUnits.months.add_duration(today, int(month.value) - today.month))
            if today.month == int(month.value):
                if not month_view:
                    cells.append(E.td(E.b(monthly(Day(pk), str(month)))))
                else:
                    cells.append(E.td(E.b(str(month))))
            else:
                cells.append(E.td(monthly(Day(pk), str(month))))
            if (i+1) % 3 == 0:
                rows.append(E.tr(*cells, align="center"))
                cells = []
        monthly_div = E.div(E.table(
            *rows, align="center"), CLASS="cal-month-table")

        header = [
            current_view(prev_month, "<<"), " " , current_view(prev_view, "<"),
            E.span(E.span("{} {}".format(monthname(today.month), today.year), E.br(), monthly_div)),
            current_view(next_view, ">"), " ", current_view(next_month, ">>")]
        elems.append(E.h2(*header, align="center"))
        weekdaysFirstLetter = " " + "".join([gettext(week.text)[0] for week in Weekdays.objects()])
        rows = [E.tr(*[E.td(E.b(day_of_week)) for day_of_week in weekdaysFirstLetter], align='center')]
        for week in CALENDAR.monthdatescalendar(today.year, today.month):
            # each week is a list of seven datetime.date objects.
            cells = []
            current_week = week[0].isocalendar()[1]
            this_week = False
            for day in week:
                pk = date2pk(day)
                link = daily(Day(pk), str(day.day))
                if day == dd.today():
                    link = E.b(link, CLASS="cal-nav-today")
                if day == today and day_view:
                    cells.append(E.td(E.b(str(day.day))))
                else:
                    cells.append(E.td(link))
                if day.isocalendar()[1] == today.isocalendar()[1]:
                    this_week = True
            else:
                cells = [
                            E.td(E.b(str(current_week)) if this_week and weekly_view else weekly(Day(pk), str(current_week)),
                                 CLASS="cal-week")
                         ] + cells
            rows.append(E.tr(*cells, align="center"))

        elems.append(E.table(*rows, align="center"))
        elems.append(E.p(daily(Day(), gettext("Today")), align="center"))
        elems.append(E.p(weekly(Day(), gettext("This week")), align="center"))
        elems.append(E.p(monthly(Day(), gettext("This month")), align="center"))

        # for o in range(-10, 10):
        #     elems.append(ar.goto_pk(o, str(o)))
        #     elems.append(" ")
        return E.div(*elems, CLASS="lino-nav-cal")

    # @classmethod
    # def get_disabled_fields(cls, obj, ar):
    #     return set()

    # @dd.displayfield(_("Date"))
    # def detail_pointer(cls, obj, ar):
    #     # print("20181230 detail_pointer() {}".format(cls))
    #     a = cls.detail_action
    #     if ar is None:
    #         return None
    #     if a is None:
    #         return None
    #     if not a.get_view_permission(ar.get_user().user_type):
    #         return None
    #     text = (str(obj),)
    #     # url = ar.renderer.get_detail_url(cls, cls.date2pk(obj))
    #     # url = ar.renderer.get_detail_url(cls, obj.pk)
    #     url = settings.SITE.kernel.default_ui.renderer.get_detail_url(cls, obj.pk)
    #     return ar.href_button(url, text)

    # @dd.displayfield(_("Date"))
    # def long_date(cls, obj, ar=None):
    #     if obj is None:
    #         return ''
    #     return dd.fdl(obj.date)



class DailyView(EventsParameters, CalendarView):
    label = _("Daily view")
    # hide_top_toolbar = True


class DailyPlannerRows(EventsParameters, dd.Table):
    model = 'cal.DailyPlannerRow'
    column_names = "seqno designation start_time end_time"
    required_roles = dd.login_required(OfficeStaff)


class DailyPlanner(DailyPlannerRows):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    label = _("Daily planner")
    editable = False
    use_detail_params_value = True

    @classmethod
    def setup_columns(self):
        names = ''
        for i, vf in enumerate(self.get_ventilated_columns()):
            self.add_virtual_field('vc' + str(i), vf)
            names += ' ' + vf.name + ':20'

        self.column_names = "overview:3 {}".format(names)

        # ~ logger.info("20131114 setup_columns() --> %s",self.column_names)

    @classmethod
    def get_ventilated_columns(cls):

        Event = rt.models.cal.Event

        def w(pc, verbose_name):
            def func(fld, obj, ar):
                # obj is the DailyPlannerRow instance
                pv = ar.param_values
                qs = Event.objects.filter(event_type__planner_column=pc)
                qs = Event.calendar_param_filter(qs, pv)
                current_day = pv.get('date',dd.today())
                if current_day:
                    qs = qs.filter(start_date=current_day)
                if obj.start_time:
                    qs = qs.filter(start_time__gte=obj.start_time,
                                   start_time__isnull=False)
                if obj.end_time:
                    qs = qs.filter(start_time__lt=obj.end_time,
                                   start_time__isnull=False)
                if not obj.start_time and not obj.end_time:
                    qs = qs.filter(start_time__isnull=True)
                qs = qs.order_by('start_time')
                chunks = [e.obj2href(ar, e.colored_calendar_fmt(pv)) for e in qs]
                return E.p(*join_elems(chunks))

            return dd.VirtualField(dd.HtmlBox(verbose_name), func)

        for pc in PlannerColumns.objects():
            yield w(pc, pc.text)


class PlannerByDay(DailyPlanner):
    master = 'cal.Day'
    # display_mode = "html"
    navigation_mode = 'day'

    @classmethod
    def get_master_instance(cls, ar, model, pk):
        return model(int(pk), ar, cls.navigation_mode)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        mi = ar.master_instance
        if mi is None:
            return []
        # filter.update()
        ar.param_values.update(date=mi.date)
        return super(PlannerByDay, cls).get_request_queryset(ar, **filter)

######################### Weekly ########################"


class WeeklyPlanner(EventsParameters, dd.Table):
    model = 'cal.DailyPlannerRow'
    # required_roles = dd.login_required(OfficeStaff)
    label = _("Weekly planner")
    editable = False
    use_detail_params_value = True

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(WeeklyPlanner, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw

    @classmethod
    def setup_columns(self):
        names = ''
        for i, vf in enumerate(self.get_ventilated_columns()):
            self.add_virtual_field('vc' + str(i), vf)
            names += ' ' + vf.name + ':20'

        self.column_names = "overview:4 {}".format(names)

    @classmethod
    def get_ventilated_columns(cls):

        Event = rt.models.cal.Event

        def w(pc, verbose_name):
            def func(fld, obj, ar):
                # obj is the DailyPlannerRow instance
                pv = ar.param_values
                qs = Event.objects.all()
                #I not sure should we use all the objects or start with filter as following !!!
                # qs = Event.objects.filter(event_type__planner_column=pc)
                qs = Event.calendar_param_filter(qs, pv)

                delata_days = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
                current_day = dd.today() + timedelta(days=delata_days)
                current_week_day = current_day + \
                    timedelta(days=int(pc.value) -
                              current_day.weekday() - 1)
                qs = qs.filter(start_date=current_week_day)
                if obj.start_time:
                    qs = qs.filter(start_time__gte=obj.start_time,
                                   start_time__isnull=False)
                if obj.end_time:
                    qs = qs.filter(start_time__lt=obj.end_time,
                                   start_time__isnull=False)
                if not obj.start_time and not obj.end_time:
                    qs = qs.filter(start_time__isnull=True)
                    link = E.p(str(current_week_day.day) if current_week_day != dd.today() else E.b(str(current_week_day.day))
                               , align="center")
                else:
                    link = ''
                qs = qs.order_by('start_time')
                chunks = [e.obj2href(ar, e.colored_calendar_fmt(pv)) for e in qs]
                return E.table(E.tr(E.td(E.div(*join_elems([link] + chunks)))),
                               CLASS="fixed-table")

            return dd.VirtualField(dd.HtmlBox(verbose_name), func)

        for pc in Weekdays.objects():
            yield w(pc, pc.text)



class WeeklyDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 cal.WeeklyPlanner:85"

class WeeklyView(EventsParameters, CalendarView):
    label = _("Weekly view")
    detail_layout = 'cal.WeeklyDetail'
    navigation_mode = "week"


######################### Monthly ########################


class MonthlyPlanner(EventsParameters, dd.VirtualTable):
    # required_roles = dd.login_required(OfficeStaff)
    label = _("Monthly planner")
    editable = False
    use_detail_params_value = True


    @classmethod
    def get_data_rows(self, ar):
        # every row in this table is a "week", i.e. a list of seven datetime.date objects
        delta_days = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
        current_day = dd.today() + timedelta(days=delta_days)
        # weeks = [week[0].isocalendar()[1] for week in CALENDAR.monthdatescalendar(current_day.year, current_day.month)]
        return CALENDAR.monthdatescalendar(current_day.year, current_day.month)
        # return weeks

    @dd.displayfield("Week")
    def week_number(cls, week, ar):
        label = str(week[0].isocalendar()[1])
        pk = date2pk(week[0])
        if ar.param_values is None:
            return None
        daily, weekly, monthly = make_link_funcs(ar)
        link = weekly(Day(pk), label)
        return E.div(*[link], align="center")

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MonthlyPlanner, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw

    @classmethod
    def setup_columns(self):
        names = ''
        for i, vf in enumerate(self.get_ventilated_columns()):
            self.add_virtual_field('vc' + str(i), vf)
            names += ' ' + vf.name + ':20'
            # names += ' ' + vf.name + (':20' if i != 0 else ":3")

        self.column_names = "week_number:3 {}".format(names)

    @classmethod
    def get_ventilated_columns(cls):

        Event = rt.models.cal.Event

        def w(pc):
            verbose_name = pc.text

            def func(fld, week, ar):
                pv = ar.param_values
                if pv is None:
                    return
                qs = Event.objects.all()
                qs = Event.calendar_param_filter(qs, pv)
                offset = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
                today = dd.today()
                current_date = dd.today(offset)
                target_day = week[int(pc.value)-1]
                qs = qs.filter(start_date=target_day)
                qs = qs.order_by('start_time')
                chunks = [E.p(e.obj2href(ar, e.colored_calendar_fmt(pv))) for e in qs]

                pk = date2pk(target_day)
                daily, weekly, monthly = make_link_funcs(ar)
                header = daily(Day(pk),str(target_day.day))
                if target_day == today:
                    header = E.b(header)
                link = E.div(header,align="center",CLASS="header")

                return E.table(E.tr(E.td(*[link,E.div(*join_elems(chunks))])),
                               CLASS="fixed-table cal-month-cell {} {} {}".format(
                                 "current-month" if current_date.month == target_day.month else "other-month",
                                 "current-day" if target_day == today else "",
                                 "cal-in-past" if target_day < today else ""
                             ))

            return dd.VirtualField(dd.HtmlBox(verbose_name), func)

        for pc in Weekdays.get_list_items():
            yield w(pc)


class MonthlyDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 cal.MonthlyPlanner:85"


class MonthlyView(EventsParameters, CalendarView):
    label = _("Monthly view")
    detail_layout = 'cal.MonthlyDetail'
    navigation_mode = "month"

