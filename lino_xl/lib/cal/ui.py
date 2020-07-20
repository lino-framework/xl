# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from collections import OrderedDict

from django.conf import settings
from django.db import models
from etgen.html import E, forcetext

from lino.api import dd, rt, _, gettext
from lino.utils import join_elems
from lino.mixins import ObservedDateRange  # todo: convert also Guests to DateRangeObservable
from lino.core.roles import Explorer
from lino.core.fields import TableRow
from lino.core import fields
from lino.utils.format_date import monthname
from lino.utils.format_date import day_and_month, day_and_weekday
from lino.modlib.users.mixins import My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator


from .choicelists import TaskStates
from .choicelists import GuestStates
from .choicelists import EntryStates
from .choicelists import AccessClasses
from .choicelists import DurationUnits
from .choicelists import EventEvents
from .mixins import daterange_text
from .utils import when_text
from .roles import CalendarReader, GuestOperator

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

    # parameters = ObservedDateRange(
    #     user=dd.ForeignKey(settings.SITE.user_model,
    #                        verbose_name=_("Managed by"),
    #                        blank=True, null=True,
    #                        help_text=_("Only rows managed by this user.")),
    #     project=dd.ForeignKey(settings.SITE.project_model,
    #                           blank=True, null=True),
    #     state=TaskStates.field(blank=True,
    #                            help_text=_("Only rows having this state.")),
    # )

    params_layout = """
    start_date end_date user state project
    """

    # @classmethod
    # def get_request_queryset(self, ar, **kwargs):
    #     # logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
    #     qs = super(Tasks, self).get_request_queryset(ar, **kwargs)
    #
    #     if ar.param_values.user:
    #         qs = qs.filter(user=ar.param_values.user)
    #
    #     if settings.SITE.project_model is not None and ar.param_values.project:
    #         qs = qs.filter(project=ar.param_values.project)
    #
    #     if ar.param_values.state:
    #         qs = qs.filter(state=ar.param_values.state)
    #
    #     if ar.param_values.start_date:
    #         qs = qs.filter(start_date__gte=ar.param_values.start_date)
    #     if ar.param_values.end_date:
    #         qs = qs.filter(start_date__lte=ar.param_values.end_date)
    #     return qs

    # @classmethod
    # def get_title_tags(self, ar):
    #     for t in super(Tasks, self).get_title_tags(ar):
    #         yield t
    #     if ar.param_values.start_date or ar.param_values.end_date:
    #         yield str(_("Dates %(min)s to %(max)s") % dict(
    #             min=ar.param_values.start_date or'...',
    #             max=ar.param_values.end_date or '...'))
    #
    #     if ar.param_values.state:
    #         yield str(ar.param_values.state)
    #
    #     # if ar.param_values.user:
    #     #     yield str(ar.param_values.user)
    #
    #     if settings.SITE.project_model is not None and ar.param_values.project:
    #         yield str(ar.param_values.project)

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
    display_mode = "summary"



class TasksByUser(Tasks):
    master_key = 'user'
    required_roles = dd.login_required(OfficeUser)


class MyTasks(Tasks):
    label = _("My tasks")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'priority start_date summary workflow_buttons project'
    params_panel_hidden = True
    # default_end_date_offset = 30 # replaced by Plugin.mytasks_end_date

    @classmethod
    def param_defaults(self, ar, **kw):
        cfg = dd.plugins.cal
        kw = super(MyTasks, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        kw.update(state=TaskStates.todo)
        if cfg.mytasks_start_date is not None:
            kw.update(start_date=settings.SITE.today(cfg.mytasks_start_date))
        if cfg.mytasks_end_date is not None:
            kw.update(end_date=settings.SITE.today(cfg.mytasks_end_date))
            # self.default_end_date_offset))
        return kw


#if settings.SITE.project_model:

class TasksByProject(Tasks):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    master_key = 'project'
    column_names = 'priority start_date user summary owner workflow_buttons *'
    display_mode = "summary"


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

    parameters = ObservedDateRange(
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

    @classmethod
    def get_create_permission(cls, ar):
        if not super(GuestsByEvent, cls).get_create_permission(ar):
            return False
        mi = ar.master_instance
        if mi and mi.can_edit_guests_manually():
            return  True
        return False

    @classmethod
    def disable_delete(cls, obj, ar):
        msg = super(GuestsByEvent, cls).disable_delete(obj, ar)
        if msg is not None:
            return msg
        mi = ar.master_instance
        if mi and mi.can_edit_guests_manually():
            return None
        return _("Guests are filled automatically.")



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
    start_date start_time end_date end_time
    every_unit every positions max_events
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

    # @classmethod
    # def get_request_queryset(self, ar, **kwargs):
    #     # print("20181121a get_request_queryset", self)
    #     qs = super(Events, self).get_request_queryset(ar, **kwargs)
    #     pv = ar.param_values
    #     return rt.models.cal.Event.calendar_param_filter(qs, pv)


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
