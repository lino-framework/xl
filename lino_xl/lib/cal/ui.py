# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
Tables for this plugin.

"""

from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _
from lino import mixins
from lino.core.roles import Explorer
from lino.modlib.users.mixins import My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator

from lino.utils import join_elems
from lino.utils.xmlgen.html import E

from .workflows import TaskStates
from .workflows import GuestStates
from .workflows import EntryStates
from .choicelists import AccessClasses
from .mixins import daterange_text
from .utils import when_text

from .roles import CalendarReader


class RemoteCalendars(dd.Table):
    model = 'cal.RemoteCalendar'
    required_roles = dd.login_required(OfficeStaff)


class Rooms(dd.Table):
    """List of rooms where calendar events can happen.

    """
    required_roles = dd.login_required((OfficeStaff, CalendarReader))
    model = 'cal.Room'
    detail_layout = """
    id name
    company contact_person
    description
    cal.EntriesByRoom
    """
    insert_layout = """
    id name
    company
    contact_person
    """

class AllRooms(Rooms):    
    required_roles = dd.login_required(OfficeStaff)


class Priorities(dd.Table):
    help_text = _("List of possible priorities of calendar events.")
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.Priority'
    column_names = 'name *'


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
    "Check whether the given subscription exists. If not, create it."
    Subscription = rt.modules.cal.Subscription
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
    help_text = _("""A calendar task is something you need to do.""")
    model = 'cal.Task'
    required_roles = dd.login_required(OfficeStaff)
    stay_in_grid = True
    column_names = 'start_date summary workflow_buttons *'
    order_by = ["start_date", "start_time"]

    detail_layout = """
    start_date due_date id workflow_buttons
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

    parameters = mixins.ObservedPeriod(
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
    def get_request_queryset(self, ar):
        # logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Tasks, self).get_request_queryset(ar)

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
            yield unicode(_("Dates %(min)s to %(max)s") % dict(
                min=ar.param_values.start_date or'...',
                max=ar.param_values.end_date or '...'))

        if ar.param_values.state:
            yield unicode(ar.param_values.state)

        # if ar.param_values.user:
        #     yield unicode(ar.param_values.user)

        if settings.SITE.project_model is not None and ar.param_values.project:
            yield unicode(ar.param_values.project)

    @classmethod
    def apply_cell_format(self, ar, row, col, recno, td):
        """
        Enhance today by making background color a bit darker.
        """
        if row.start_date == settings.SITE.today():
            td.attrib.update(bgcolor="gold")


class TasksByController(Tasks):
    master_key = 'owner'
    required_roles = dd.login_required(OfficeUser)
    column_names = 'start_date summary workflow_buttons id'
    # hidden_columns = set('owner_id owner_type'.split())
    auto_fit_column_widths = True


class TasksByUser(Tasks):
    """
    Shows the list of tasks for this user.
    """
    master_key = 'user'
    required_roles = dd.login_required(OfficeUser)


class MyTasks(Tasks):
    """All my tasks.  Only those whose start_date is today or in the
    future.

    """
    label = _("My tasks")
    required_roles = dd.login_required(OfficeUser)
    help_text = _("Table of all my tasks.")
    column_names = 'start_date summary workflow_buttons project'
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
        kw.update(start_date=settings.SITE.today())
        kw.update(end_date=settings.SITE.today(
            self.default_end_date_offset))
        return kw


#if settings.SITE.project_model:

class TasksByProject(Tasks):
    required_roles = dd.login_required(OfficeUser)
    master_key = 'project'
    column_names = 'start_date user summary workflow_buttons *'


class GuestRoles(dd.Table):
    help_text = _("The role of a guest expresses what the "
                  "partner is going to do there.")
    model = 'cal.GuestRole'
    required_roles = dd.login_required(dd.SiteStaff, OfficeUser)
    detail_layout = """
    id name
    #build_method #template #email_template #attach_to_email
    cal.GuestsByRole
    """


class Guests(dd.Table):
    "The default table for :class:`Guest`."
    help_text = _("""A guest is a partner invited to an event. """)
    model = 'cal.Guest'
    required_roles = dd.login_required(dd.SiteStaff, OfficeUser)
    column_names = 'partner role workflow_buttons remark event *'
    stay_in_grid = True
    detail_layout = """
    event partner role
    state remark workflow_buttons
    # outbox.MailsByController
    """
    insert_layout = dd.InsertLayout("""
    event
    partner
    role
    """, window_size=(60, 'auto'))

    parameters = mixins.ObservedPeriod(
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
            help_text=_("Only rows having this event state.")),
        guest_state=GuestStates.field(
            blank=True,
            verbose_name=_("Guest state"),
            help_text=_("Only rows having this guest state.")),
    )

    params_layout = """start_date end_date user event_state guest_state
    project partner"""

    @classmethod
    def get_request_queryset(self, ar):
        # logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Guests, self).get_request_queryset(ar)

        if isinstance(qs, list):
            return qs

        if ar.param_values.user:
            qs = qs.filter(event__user=ar.param_values.user)
        if settings.SITE.project_model is not None and ar.param_values.project:
            qs = qs.filter(event__project=ar.param_values.project)

        if ar.param_values.event_state:
            qs = qs.filter(event__state=ar.param_values.event_state)

        if ar.param_values.guest_state:
            qs = qs.filter(state=ar.param_values.guest_state)

        if ar.param_values.partner:
            qs = qs.filter(partner=ar.param_values.partner)

        if ar.param_values.start_date:
            if ar.param_values.end_date:
                qs = qs.filter(
                    event__start_date__gte=ar.param_values.start_date)
            else:
                qs = qs.filter(event__start_date=ar.param_values.start_date)
        if ar.param_values.end_date:
            qs = qs.filter(event__end_date__lte=ar.param_values.end_date)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Guests, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.start_date or pv.end_date:
            yield unicode(_("Dates %(min)s to %(max)s") % dict(
                min=pv.start_date or'...',
                max=pv.end_date or '...'))

        if pv.event_state:
            yield unicode(pv.event_state)

        if pv.partner:
            yield unicode(pv.partner)

        if pv.guest_state:
            yield unicode(pv.guest_state)

        # if pv.user:
        #     yield unicode(pv.user)

        if settings.SITE.project_model is not None and pv.project:
            yield unicode(pv.project)

class AllGuests(Guests):
    required_roles = dd.login_required(Explorer)

class GuestsByEvent(Guests):
    master_key = 'event'
    required_roles = dd.login_required(OfficeUser)
    auto_fit_column_widths = True
    column_names = 'partner role workflow_buttons'


class GuestsByRole(Guests):
    master_key = 'role'
    required_roles = dd.login_required(OfficeUser)


class GuestsByPartner(Guests):
    label = _("Presences")
    master_key = 'partner'
    required_roles = dd.login_required(OfficeUser)
    column_names = 'event__when_text workflow_buttons'
    auto_fit_column_widths = True

    slave_grid_format = "summary"

    @classmethod
    def get_slave_summary(self, obj, ar):
        """The summary view for this table.

        See :meth:`lino.core.actors.Actor.get_slave_summary`.

        """
        if ar is None:
            return ''
        sar = self.request_from(ar, master_instance=obj)

        elems = []
        for guest in sar:
            lbl = dd.fds(guest.event.start_date)
            if guest.state.button_text:
                lbl = "{0}{1}".format(lbl, guest.state.button_text)
            elems.append(ar.obj2html(guest.event, lbl))
        elems = join_elems(elems, sep=', ')
        return ar.html_text(E.div(*elems))
        # return E.div(class_="htmlText", *elems)

class MyPresences(Guests):
    """Shows all my presences in calendar events, independently of their
    state.

    """
    required_roles = dd.login_required(OfficeUser)
    order_by = ['event__start_date', 'event__start_time']
    label = _("My presences")
    column_names = 'event__start_date event__start_time event_summary role workflow_buttons remark *'
    params_panel_hidden = True

    @classmethod
    def get_request_queryset(self, ar):
        # logger.info("20130809 MyPresences")
        if ar.get_user().partner is None:
            raise Warning("Action not available for users without partner")
        return super(MyPresences, self).get_request_queryset(ar)

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
    help_text = _(
        """Received invitations which I must accept or reject.""")
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
    order_by = ['event__start_date', 'event__start_time']
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
    help_text = _("""The list of Event Types defined on this system.
    An EventType is a list of events which have certain things in common,
    especially they are displayed in the same colour in the calendar panel.
    """)
    required_roles = dd.login_required(OfficeStaff)
    model = 'cal.EventType'
    column_names = "name *"

    detail_layout = """
    name
    event_label
    # description
    start_date max_days id
    # type url_template username password
    #build_method #template email_template attach_to_email
    is_appointment all_rooms locks_user max_conflicting
    EntriesByType
    """

    insert_layout = dd.InsertLayout("""
    name
    event_label
    """, window_size=(60, 'auto'))


class RecurrentEvents(dd.Table):
    """The list of all recurrent events (:class:`RecurrentEvent`).

    """
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
    # description
    GuestsByEvent #outbox.MailsByController
    """


class EventEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = EventEvents.add_item
add('10', _("Stable"), 'stable')
add('20', _("Unstable"), 'pending')


class Events(dd.Table):
    """Table which shows all calendar events.

    .. attribute:: show_appointments

        Whether only :term:`appointments <appointment>` should be
        shown.  "Yes" means only appointments, "No"
        means no appointments and leaving it to blank shows both types
        of events.

        An appointment is an event whose *event type* has
        :attr:`appointment
        <lino_xl.lib.cal.models.EventType.appointment>` checked.

    """

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

    detail_layout = EventDetail()
    insert_layout = """
    start_date start_time end_date end_time
    summary
    # room priority access_class transparent
    """

    detail_html_template = "cal/Event/detail.html"


    params_panel_hidden = True

    parameters = mixins.ObservedPeriod(
        user=dd.ForeignKey(settings.SITE.user_model,
                           verbose_name=_("Managed by"),
                           blank=True, null=True,
                           help_text=_("Only rows managed by this user.")),
        project=dd.ForeignKey(settings.SITE.project_model,
                              blank=True, null=True),
        event_type=dd.ForeignKey('cal.EventType', blank=True, null=True),
        room=dd.ForeignKey('cal.Room', blank=True, null=True),
        assigned_to=dd.ForeignKey(settings.SITE.user_model,
                                  verbose_name=_("Assigned to"),
                                  blank=True, null=True,
                                  help_text=_(
                                      "Only events assigned to this user.")),
        state=EntryStates.field(blank=True,
                                help_text=_("Only rows having this state.")),
        # unclear = models.BooleanField(_("Unclear events"))
        observed_event=EventEvents.field(blank=True),
        show_appointments=dd.YesNo.field(_("Appointments"), blank=True),
    )

    params_layout = """
    start_date end_date observed_event state
    user assigned_to project event_type room show_appointments
    """
    # ~ next = NextDateAction() # doesn't yet work. 20121203

    fixed_states = set(EntryStates.filter(fixed=True))
    # pending_states = set([es for es in EntryStates if not es.fixed])
    pending_states = set(EntryStates.filter(fixed=False))

    @classmethod
    def get_request_queryset(self, ar):
        # logger.info("20121010 Clients.get_request_queryset %s",ar.param_values)
        qs = super(Events, self).get_request_queryset(ar)
        pv = ar.param_values

        if pv.user:
            qs = qs.filter(user=pv.user)
        if pv.assigned_to:
            qs = qs.filter(assigned_to=pv.assigned_to)

        if settings.SITE.project_model is not None and pv.project:
            qs = qs.filter(project=pv.project)

        if pv.event_type:
            qs = qs.filter(event_type=pv.event_type)
        else:
            if pv.show_appointments == dd.YesNo.yes:
                qs = qs.filter(event_type__is_appointment=True)
            elif pv.show_appointments == dd.YesNo.no:
                qs = qs.filter(event_type__is_appointment=False)

        if pv.state:
            qs = qs.filter(state=pv.state)

        if pv.room:
            qs = qs.filter(room=pv.room)

        if pv.observed_event == EventEvents.stable:
            qs = qs.filter(state__in=self.fixed_states)
        elif pv.observed_event == EventEvents.pending:
            qs = qs.filter(state__in=self.pending_states)

        if pv.start_date:
            qs = qs.filter(start_date__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(start_date__lte=pv.end_date)
        return qs

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
            yield unicode(pv.state)

        if pv.event_type:
            yield unicode(pv.event_type)

        # if pv.user:
        #     yield unicode(pv.user)

        if pv.room:
            yield unicode(pv.room)

        if settings.SITE.project_model is not None and pv.project:
            yield unicode(pv.project)

        if pv.assigned_to:
            yield unicode(self.parameters['assigned_to'].verbose_name) \
                + ' ' + unicode(pv.assigned_to)

    @classmethod
    def apply_cell_format(self, ar, row, col, recno, td):
        """
        Enhance today by making background color a bit darker.
        """
        if row.start_date == settings.SITE.today():
            td.attrib.update(bgcolor="#bbbbbb")

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(Events, self).param_defaults(ar, **kw)
        kw.update(start_date=settings.SITE.site_config.hide_events_before)
        return kw

    
class AllEntries(Events):
    required_roles = dd.login_required(Explorer)

class EntriesByType(Events):
    master_key = 'event_type'


class ConflictingEvents(Events):
    """Shows events conflicting with this one (the master).
    
    """
    label = ' ⚔ '  # 2694
    help_text = _("Show events conflicting with this one.")

    master = 'cal.Event'
    column_names = 'start_date start_time end_time project room user *'

    @classmethod
    def get_request_queryset(self, ar, **kw):
        qs = ar.master_instance.get_conflicting_events()
        if qs is None:
            return rt.modules.cal.Event.objects.none()
        return qs
    

class PublicEntries(Events):
    required_roles = dd.login_required(CalendarReader)
    
    column_names = 'overview room event_type  *'
    filter = models.Q(access_class=AccessClasses.public)
    
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(PublicEntries, self).param_defaults(ar, **kw)
        # kw.update(show_appointments=dd.YesNo.yes)
        kw.update(start_date=settings.SITE.today())
        # kw.update(end_date=settings.SITE.today())
        return kw



class EntriesByDay(Events):
    """
    This table is usually labelled "Appointments today". It has no
    "date" column because it shows events of a given date.

    The default filter parameters are set to show only
    :term:`appointments <appointment>`.

    """
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
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
    Displays the :class:`Events <Event>` at a given :class:`Room`.
    """
    master_key = 'room'


class EntriesByController(Events):
    """Shows the events linked to this database object.

    If the master is an :class:`EventGenerator
    <lino_xl.lib.cal.mixins.EventGenerator>`, then this includes
    especially the events which were automatically generated.

    """
    required_roles = dd.login_required(OfficeUser)
    master_key = 'owner'
    column_names = 'when_html summary workflow_buttons *'
    # column_names = 'when_text:20 when_html summary workflow_buttons *'
    auto_fit_column_widths = True
    slave_grid_format = "summary"

    @classmethod
    def get_slave_summary(self, obj, ar):
        """The summary view for this table.

        See :meth:`lino.core.actors.Actor.get_slave_summary`.

        """
        if ar is None:
            return ''
        sar = self.request_from(ar, master_instance=obj)

        fmt = obj.get_date_formatter()

        elems = []
        for evt in sar:
            # if len(elems) > 0:
            #     elems.append(', ')
            elems.append(' ')
            if evt.auto_type:
                # elems.append("({}) ".format(evt.auto_type))
                elems.append("{}: ".format(evt.auto_type))

            lbl = fmt(evt.start_date)
            if evt.state.button_text:
                lbl = "{0}{1}".format(lbl, evt.state.button_text)
            elems.append(ar.obj2html(evt, lbl))
        # elems = join_elems(elems, sep=', ')
        toolbar = []
        ar1 = obj.do_update_events.request_from(sar)
        if ar1.get_permission():
            btn = ar1.ar2button(obj)
            toolbar.append(btn)

        ar2 = self.insert_action.request_from(sar)
        if ar2.get_permission():
            btn = ar2.ar2button()
            toolbar.append(btn)

        if len(toolbar):
            toolbar = join_elems(toolbar, sep=' ')
            elems.append(E.p(*toolbar))

        return ar.html_text(E.div(*elems))
    

if settings.SITE.project_model:

    class EntriesByProject(Events):
        required_roles = dd.login_required(OfficeUser)
        master_key = 'project'
        auto_fit_column_widths = True
        stay_in_grid = True
        column_names = 'when_html user summary workflow_buttons'
        # column_names = 'when_text user summary workflow_buttons'


class OneEvent(Events):
    """Show a single calendar event."""
    show_detail_navigator = False
    use_as_default_table = False
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    # required_roles = dd.login_required(OfficeUser)


class MyEntries(Events):
    """Table which shows today's and all future appointments of the
    requesting user.  The default filter parameters are set to show
    only :term:`appointments <appointment>`.

    """
    label = _("My appointments")
    help_text = _("Table of my appointments.")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'overview project #event_type #summary workflow_buttons *'
    auto_fit_column_widths = True

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
    """Like :class:`MyEntries`, but only today."""
    label = _("My appointments today")
    column_names = 'start_time end_time project event_type '\
                   'summary workflow_buttons *'

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyEntriesToday, self).param_defaults(ar, **kw)
        kw.update(end_date=dd.today())
        return kw



class MyAssignedEvents(MyEntries):
    """
    The table of events which are *assigned* to me. That is, whose
    :attr:`Event.assigned_to` field refers to the requesting user.

    This table also causes a :term:`welcome message` "X events have been
    assigned to you" in case it is not empty.

    """
    label = _("Events assigned to me")
    help_text = _("Table of events assigned to me.")
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
            txt = _("%d events have been assigned to you.") % count
            yield ar.href_to_request(sar, txt)


class OverdueAppointments(Events):
    """Shows **overdue appointments**, i.e. appointments whose date is
    over but who are still in a nonstable state.

    :attr:`show_appointments` is set to "Yes", :attr:`observed_event`
    is set to "Unstable", :attr:`end_date` is set to today.

    """
    required_roles = dd.login_required(OfficeStaff)
    label = _("Overdue appointments")
    column_names = 'when_html user project owner event_type summary workflow_buttons *'
    auto_fit_column_widths = True
    params_panel_hidden = False

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(OverdueAppointments, self).param_defaults(ar, **kw)
        kw.update(observed_event=EventEvents.pending)
        kw.update(end_date=settings.SITE.today())
        kw.update(show_appointments=dd.YesNo.yes)
        return kw

class MyOverdueAppointments(My, OverdueAppointments):
    """Like OverdueAppointments, but only for myself.

    """
    label = _("My overdue appointments")
    required_roles = dd.login_required(OfficeUser)
    column_names = 'overview project owner event_type workflow_buttons *'

class MyUnconfirmedAppointments(MyEntries):
    """Shows appointments in the near future which are still in draft
    state.

    :attr:`show_appointments` is set to "Yes", :attr:`state`
    is set to "Draft", :attr:`start_date` is set to today.

    """
    required_roles = dd.login_required(OfficeUser)
    label = _("Unconfirmed appointments")
    column_names = 'when_html project summary workflow_buttons *'
    auto_fit_column_widths = True
    params_panel_hidden = False

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyUnconfirmedAppointments, self).param_defaults(ar, **kw)
        kw.update(observed_event=EventEvents.pending)
        kw.update(state=EntryStates.draft)
        kw.update(start_date=settings.SITE.today())
        kw.update(end_date=settings.SITE.today(14))
        kw.update(show_appointments=dd.YesNo.yes)
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

    
