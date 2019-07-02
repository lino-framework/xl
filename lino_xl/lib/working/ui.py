# -*- coding: UTF-8 -*-
# Copyright 2011-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import six

import sys
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import naturaltime

from lino_xl.lib.cal.utils import when_text
from lino.api import dd, rt, _

from lino_xl.lib.tickets.ui import Tickets

from lino.utils import ONE_DAY
from etgen.html import E, join_elems, forcetext
from lino.utils.quantities import Duration
from lino.modlib.system.choicelists import ObservedEvent
from lino.mixins.periods import ObservedDateRange

from lino_xl.lib.tickets.roles import Triager, TicketsStaff
from lino_xl.lib.tickets.choicelists import (
    TicketEvents, TicketStates)

from .roles import Worker
from .choicelists import ReportingTypes


class TOTAL_KEY(object):
    pass

MIN_DURATION = Duration('0:01')

def ensureUtf(s):
    if sys.version_info < (3,):
        return unicode(s)
    else:
        return str(s)

class TicketHasSessions(ObservedEvent):
    text = _("Has been worked on")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(sessions_by_ticket__start_date__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(sessions_by_ticket__start_date__lte=pv.end_date)
        qs = qs.annotate(num_sessions=Count('sessions_by_ticket'))
        qs = qs.filter(num_sessions__gt=0)
        return qs

TicketEvents.add_item_instance(TicketHasSessions("working"))


# class ProjectHasSessions(ObservedEvent):
#     text = _("Has been worked on")

#     def add_filter(self, qs, pv):
#         if pv.start_date:
#             qs = qs.filter(
#                 tickets_by_project__sessions_by_ticket__start_date__gte=
#                 pv.start_date)
#         if pv.end_date:
#             qs = qs.filter(
#                 tickets_by_project__sessions_by_ticket__end_date__lte=
#                 pv.end_date)
#         qs = qs.annotate(num_sessions=Count(
#             'tickets_by_project__sessions_by_ticket'))
#         qs = qs.filter(num_sessions__gt=0)
#         return qs

# ProjectEvents.add_item_instance(ProjectHasSessions("working"))


class SessionTypes(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = 'working.SessionType'
    column_names = 'name *'


class Sessions(dd.Table):
    required_roles = dd.login_required(Worker)
    model = 'working.Session'
    column_names = 'ticket user start_date start_time end_date end_time '\
                   'break_time summary duration ticket_no  *'

    detail_layout = """
    ticket:40 user:20 faculty:20 reporting_type:10
    start_date start_time end_date end_time break_time duration
    summary:60 is_fixing workflow_buttons:20
    description
    """
    insert_layout = """
    ticket
    summary
    session_type
    """

    order_by = ['-start_date', '-start_time', 'id']
    # order_by = ['start_date', 'start_time']
    # stay_in_grid = True
    parameters = ObservedDateRange(
        company=dd.ForeignKey(
            'contacts.Company', null=True, blank=True),
        # project=dd.ForeignKey(
        #     'tickets.Project', null=True, blank=True),
        site=dd.ForeignKey(
            'tickets.Site', null=True, blank=True),
        # ticket=dd.ForeignKey(
        #     dd.plugins.working.ticket_model, null=True, blank=True),
        # user=dd.ForeignKey('users.User', null=True, blank=True),
        session_type=dd.ForeignKey(
            'working.SessionType', null=True, blank=True),
        observed_event=dd.PeriodEvents.field(
            blank=True, default=dd.PeriodEvents.as_callable('active')),
    )

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(Sessions, cls).get_simple_parameters())
        s += ['session_type', 'ticket']
        return s

    params_layout = """
    start_date end_date observed_event company #project
    user session_type ticket site
    """
    auto_fit_column_widths = True

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Sessions, self).get_request_queryset(ar)
        pv = ar.param_values
        ce = pv.observed_event
        if ce is not None:
            qs = ce.add_filter(qs, pv)

        # if pv.project:
        #     qs = qs.filter(ticket__project__in=pv.project.whole_clan())

        if pv.site:
            qs = qs.filter(ticket__site=pv.site)

        if pv.company:
            qs = qs.filter(ticket__site__company=pv.company)
            # if dd.is_installed('deploy'):
            #     qs = qs.filter(
            #         ticket__deployments_by_ticket__milestone__room__company=pv.company)
            # else:
            #     qs = qs.filter(ticket__project__company=pv.company)


        return qs


class SessionsByTicket(Sessions):
    master_key = 'ticket'
    column_names = 'start_date summary start_time end_time  '\
                   'break_time duration user is_fixing *'
    display_mode = 'summary'

    @classmethod
    def get_table_summary(self, obj, ar):
        if ar is None:
            return ''
        elems = []

        # Button for starting a session from ticket
        sar = obj.start_session.request_from(ar)
        # if ar.renderer.is_interactive and sar.get_permission():
        # if sar.get_permission():
        #     btn = sar.ar2button(obj)
        #     elems += [E.p(btn)]

        # Active sessions:
        active_sessions = []
        session_summaries = E.ul()
        qs = rt.models.working.Session.objects.filter(ticket=obj)
        tot = Duration()
        for ses in qs:
            d = ses.get_duration()
            if d is not None:
                tot += d
            if ses.end_time is None:
                txt = "{0} since {1}".format(ses.user, ses.start_time)
                lnk = ar.obj2html(ses, txt)
                sar = ses.end_session.request_from(ar)
                if sar.get_permission():
                    lnk = E.span(lnk, " ", sar.ar2button(ses))
                active_sessions.append(lnk)
            if ses.summary:
                session_summaries.insert(0,
                    E.li(
                        "%s %s: %s"%(ses.user,
                                     naturaltime(datetime.combine(
                                                 ses.start_date, ses.start_time))
                                     ,ses.summary)
                    )
                )


        # elems.append(E.p(_("Total {0} hours.").format(tot)))
        elems.append(E.p(_("Total %s hours.") % tot))

        if len(active_sessions) > 0:
            elems.append(E.p(
                ensureUtf(_("Active sessions")), ": ",
                *join_elems(active_sessions, ', ')))
        if len(session_summaries) > 0:
            elems.append(session_summaries)

        return ar.html_text(E.div(*elems))


class SessionsBySite(Sessions):
    master_key = 'ticket__site'
    column_names = 'start_date summary start_time end_time  '\
                   'break_time duration user is_fixing *'
    
class MySessions(Sessions):
    column_names = 'start_date start_time end_time '\
                   'break_time duration ticket_no ticket__site summary *'

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MySessions, self).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw


class MySessionsByDate(MySessions):
    order_by = ['start_date', 'start_time']
    label = _("My sessions by date")
    column_names = (
        'start_time:5 end_time:5 break_time:6 duration:5 summary ticket '
        'site_ref:10 workflow_buttons:10 *')

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MySessionsByDate, self).param_defaults(ar, **kw)
        kw.update(start_date=dd.today())
        kw.update(end_date=dd.today())
        return kw

    @classmethod
    def create_instance(self, ar, **kw):
        kw.update(start_date=ar.param_values.start_date)
        return super(MySessions, self).create_instance(ar, **kw)

from lino_xl.lib.cal.models import Day

class MySessionsByDay(MySessionsByDate):

    master = Day
    # display_mode = "html"
    # use_detail_params_value = True

    @classmethod
    def get_master_instance(cls, ar, model, pk):
        return model(int(pk))

    @classmethod
    def get_request_queryset(cls, ar, **flt):
        mi = ar.master_instance
        if mi is None:
            return []
        pv = ar.param_values
        pv.update(start_date=mi.date, end_date=mi.date)
        pv.update(observed_event=dd.PeriodEvents.started)
        if mi.ar is not None:
            pv.update(user=mi.ar.get_user() if (mi.ar.param_values is None or
                                                mi.ar.param_values.user is None
                                                )else mi.ar.param_values.user)
        return super(MySessionsByDay, cls).get_request_queryset(ar, **flt)


def load_sessions(self, sar):
    self._root2tot = {}
    self._tickets = set()
    grand_tot = Duration()
    for ses in sar:
        self._tickets.add(ses.ticket)
        d = ses.get_duration() or MIN_DURATION
        grand_tot += d
        # root = ses.get_root_project()
        root = ses.get_reporting_type()
        # if ses.ticket:
        #     root = ses.ticket.reporting_type
        # else:
        #     root = None
        tot = self._root2tot.get(root, Duration()) + d
        self._root2tot[root] = tot

    self._root2tot[TOTAL_KEY] = grand_tot


def compute_invested_time(obj, **spv):
    # spv = dict(start_date=pv.start_date, end_date=pv.end_date)
    spv.update(observed_event=dd.PeriodEvents.started)
    sar = SessionsByTicket.request(master_instance=obj, param_values=spv)
    tot = Duration()
    for obj in sar:
        d = obj.get_duration()
        if d is not None:
            tot += d
    return tot


class InvestedTime(dd.Table):
    @dd.virtualfield(dd.DurationField(_("Time")))
    def invested_time(cls, obj, ar):
        return obj._invested_time

    @dd.displayfield(_("Description"))
    def my_description(cls, obj, ar):
        mi = ar.master_instance
        if mi is None:
            return
        lst = [obj.summary]
        tpl = u"{0}: {1}"
        # if obj.site is not None and obj.site == mi.interesting_for:
        #     lst.append(_("site-specific"))
        if obj.site is not None:  # and obj.site != mi.interesting_for:
            lst.append(tpl.format(
                ensureUtf(_("Site")), ensureUtf(obj.site)))
        if obj.user is not None:
            lst.append(tpl.format(
                ensureUtf(_("Author")), ensureUtf(obj.user)))
        # if obj.project is not None:
        #     lst.append(tpl.format(
        #         ensureUtf(_("Project")), ensureUtf(obj.project)))
        # if obj.topic is not None:
        #     lst.append(tpl.format(
        #         ensureUtf(_("Topic")), ensureUtf(obj.topic)))
        return E.p(*join_elems(lst, '. '))


def rpttype2vf(func, rpttype, verbose_name):
    return dd.VirtualField(dd.DurationField(verbose_name), func)

from lino.core.tables import VentilatedColumns

# class WorkedHours(dd.VentilatingTable):
#     """
#     A table showing one row per day with a summary view of the sessions
#     on that day.
#     """
#     required_roles = dd.login_required(Worker)
#     label = _("Worked hours")
#     hide_zero_rows = True
#     parameters = ObservedDateRange(
#         user=dd.ForeignKey('users.User', null=True, blank=True))
#     params_layout = "start_date end_date user"
#     # editable = False
#     auto_fit_column_widths = True
#
#     class Row(object):
#         def __init__(self, ar, day):
#             self.day = day
#             pv = dict(start_date=day, end_date=day)
#             pv.update(observed_event=dd.PeriodEvents.started)
#             pv.update(user=ar.param_values.user)
#             self.sar = ar.spawn(MySessionsByDate, param_values=pv)
#             load_sessions(self, self.sar)
#
#         def __unicode__(self):
#             return when_text(self.day)
#
#         def __repr__(self):
#             return when_text(self.day)
#
#     @dd.displayfield(_("Description"))
#     def description(self, obj, ar):
#         # pv = dict(start_date=obj.day, end_date=obj.day)
#         # pv.update(observed_event=dd.PeriodEvents.active)
#         # pv.update(user=ar.param_values.user)
#         # sar = ar.spawn(MySessionsByDate, param_values=pv)
#         elems = [obj.sar.ar2button(label=six.text_type(obj))]
#         tickets = [
#             ar.obj2html(t, "#{0}".format(t.id), title=t.summary)
#             for t in obj._tickets]
#         if len(tickets) > 0:
#             elems.append(" (")
#             elems += join_elems(tickets, ', ')
#             elems.append(")")
#         return E.span(*elems)
#
#     @classmethod
#     def get_data_rows(cls, ar):
#         pv = ar.param_values
#         start_date = pv.start_date or dd.today(-7)
#         end_date = pv.end_date or dd.today(7)
#         d = end_date
#         while d > start_date:
#             yield cls.Row(ar, d)
#             d -= ONE_DAY
#
#     @dd.displayfield("Date")
#     def date(cls, row, ar):
#         return dd.fdl(row.day)
#
#     @classmethod
#     def param_defaults(cls, ar, **kw):
#         kw = super(WorkedHours, cls).param_defaults(ar, **kw)
#         kw.update(start_date=dd.today(-7))
#         kw.update(end_date=dd.today())
#         kw.update(user=ar.get_user())
#         return kw
#
#     @classmethod
#     def get_ventilated_columns(cls):
#
#         def w(rpttype, verbose_name):
#             def func(fld, obj, ar):
#                 return obj._root2tot.get(rpttype, None)
#             return dd.VirtualField(dd.DurationField(verbose_name), func)
#
#         for rpttype in ReportingTypes.objects():
#             yield w(rpttype, six.text_type(rpttype))
#         # yield w(None, _("N/A"))
#         yield w(TOTAL_KEY, _("Total"))



class DurationReport(VentilatedColumns):
    
    abstract = True
    
    @classmethod
    def get_ventilated_columns(cls):
        # yield the fields to be insered at {vcolumns} in template
        def w(rpttype, verbose_name):
            def func(fld, obj, ar):
                return obj._root2tot.get(rpttype, None)
            return dd.VirtualField(dd.DurationField(verbose_name), func)
        
        # def w(rpttype, verbose_name):
        #     def func(fld, obj, ar):
        #         if obj.get_reporting_type() == rpttype:
        #             return obj.get_duration()
        #         return None
        #     return dd.VirtualField(dd.DurationField(verbose_name), func)

        for rpttype in ReportingTypes.objects():
            yield w(rpttype, six.text_type(rpttype))
        # yield w(None, _("N/A"))

class SessionsByReport(Sessions, DurationReport):
    master = 'working.ServiceReport'
    
    column_names_template = "start_date start_time end_time break_time " \
                            "my_description:50 user {vcolumns} *"

    order_by = ['start_date', 'start_time', 'id']
    
    # @classmethod
    # def get_data_rows(cls, ar):
    #     for ses in cls.get_request_queryset(ar):
    #         load_sessions(ses, [ses])
    #         yield ses

    @classmethod
    def get_row_by_pk(cls, ar, pk): # fixes #2434
        obj = super(SessionsByReport, cls).get_row_by_pk(ar, pk)
        if obj is not None:
            load_sessions(obj, [obj])
        return obj
        
    @classmethod
    def get_request_queryset(self, ar):
        mi = ar.master_instance
        if mi is None:
            return
        spv = dict(start_date=mi.start_date, end_date=mi.end_date)
        # spv = mi.get_tickets_parameters()
        spv.update(company=mi.interesting_for)
        spv.update(observed_event=dd.PeriodEvents.started)
        spv.update(user=mi.user)
        ar.param_values.update(spv)

        qs = super(SessionsByReport, self).get_request_queryset(ar)
        for obj in qs:
            load_sessions(obj, [obj])
            # obj._invested_time = compute_invested_time(
            #     obj, start_date=mi.start_date, end_date=mi.end_date,
            #     user=mi.user)
            if obj._root2tot.get(TOTAL_KEY):
                yield obj

    @dd.displayfield(_("Description"))
    def my_description(self, obj, ar):
        elems = [obj.summary]
        t = obj.ticket
        elems += [" ", 
            ar.obj2html(t, "#{0}".format(t.id), title=t.summary)]
        return E.p(*elems)


class TicketsByReport(Tickets, DurationReport):
    """The list of tickets mentioned in a service report."""
    master = 'working.ServiceReport'
    # column_names = "summary id reporter #project product site state
    # invested_time"
    column_names_template = "id detail_link end_user site state {vcolumns}"
    order_by = ['id']

    @classmethod
    def get_request_queryset(self, ar):
        mi = ar.master_instance
        if mi is None:
            return
        pv = ar.param_values

        pv.update(start_date=mi.start_date, end_date=mi.end_date)
        pv.update(interesting_for=mi.interesting_for)
        pv.update(observed_event=TicketEvents.working)

        spv = dict(start_date=mi.start_date, end_date=mi.end_date)
        spv.update(observed_event=dd.PeriodEvents.started)
        spv.update(user=mi.user)
        qs = super(TicketsByReport, self).get_request_queryset(ar)
        for obj in qs:
            sar = SessionsByTicket.request(
                master_instance=obj, param_values=spv)
            load_sessions(obj, sar)
            # obj._invested_time = compute_invested_time(
            #     obj, start_date=mi.start_date, end_date=mi.end_date,
            #     user=mi.user)
            if obj._root2tot.get(TOTAL_KEY):
                yield obj

from lino_xl.lib.tickets.ui import Sites

class SitesByReport(Sites, DurationReport):
    master = 'working.ServiceReport'
    # column_names = "summary id reporter #project product site state
    # invested_time"
    column_names_template = "name parsed_description {vcolumns}"
    order_by = ['name']

    @classmethod
    def get_request_queryset(self, ar):
        mi = ar.master_instance
        if mi is None:
            return
        pv = ar.param_values

        pv.update(start_date=mi.start_date, end_date=mi.end_date)
        pv.update(interesting_for=mi.interesting_for)
        pv.update(observed_event=TicketEvents.working)

        spv = dict(start_date=mi.start_date, end_date=mi.end_date)
        spv.update(observed_event=dd.PeriodEvents.started)
        spv.update(user=mi.user)
        # qs = super(SitesByReport, self).get_request_queryset(ar)
        
        qs = rt.models.tickets.Site.objects.filter(
            company=mi.interesting_for)
        for obj in qs:
            sar = SessionsBySite.request(
                master_instance=obj, param_values=spv)
            load_sessions(obj, sar)
            # obj._invested_time = compute_invested_time(
            #     obj, start_date=mi.start_date, end_date=mi.end_date,
            #     user=mi.user)
            if obj._root2tot.get(TOTAL_KEY):
                yield obj


# from lino.modlib.users.desktop import Users

# class WorkersByReport(Users, DurationReport):

#     @classmethod
#     def get_request_queryset(self, ar):
#         mi = ar.master_instance
#         if mi is None:
#             return
#         pv = ar.param_values

#         # pv.update(start_date=mi.start_date, end_date=mi.end_date)
#         # pv.update(interesting_for=mi.interesting_for)
#         # pv.update(observed_event=TicketEvents.working)

#         spv = dict(start_date=mi.start_date, end_date=mi.end_date)
#         spv.update(observed_event=dd.PeriodEvents.started)
#         spv.update(user=mi.user)
#         # qs = super(SitesByReport, self).get_request_queryset(ar)
#         workers = (ut for ut in UserTypes.get_list_items()
#                    if ut.has_required_roles([Worker]))
#         qs = rt.models.users.User.objects.filter(
#             user_type__in=workers)
#         for obj in qs:
#             sar = SessionsByUser.request(
#                 interesting_for=
#                 master_instance=obj, param_values=spv)
#             load_sessions(obj, sar)
#             if obj._root2tot.get(TOTAL_KEY):
#                 yield obj


    

class ServiceReports(dd.Table):
    """List of service reports."""
    required_roles = dd.login_required(Worker)

    model = "working.ServiceReport"
    insert_layout = """
    start_date end_date 
    interesting_for
    """
    detail_layout = """
    id start_date end_date user interesting_for ticket_state printed
    company contact_person
    SessionsByReport
    # TicketsByReport
    # ProjectsByReport
    # CoursesByReport
    """
    column_names = "start_date end_date user interesting_for "\
                   "ticket_state printed *"

    params_panel_hidden = True
    order_by = ['-start_date']


class ReportsByPartner(ServiceReports):
    """List of service reports issued for a given site."""
    master_key = 'interesting_for'


class SummaryTable(dd.Table):
    allow_create = False
    hide_sums = True



class SiteSummaries(SummaryTable):
    model = 'working.SiteSummary'
    detail_layout = """
    master year month
    active_tickets inactive_tickets id
    *
    """


class AllSummaries(SiteSummaries):
    """Lists all summary records for all sites."""
    required_roles = dd.login_required(TicketsStaff)


class SummariesBySite(SiteSummaries):
    master_key = 'master'
    auto_fit_column_widths = True
    required_roles = dd.login_required(Triager)

    @classmethod
    def setup_columns(cls):
        cls.column_names = "year "
        cls.column_names += ' '.join(cls.model.get_summary_columns())


class UserSummaries(SummaryTable):
    model = 'working.UserSummary'
    detail_layout = """
    master year month id
    *
    """


class SummariesByUser(UserSummaries):
    master_key = 'master'
    auto_fit_column_widths = True
    required_roles = dd.login_required(Triager)

    @classmethod
    def setup_columns(cls):
        cls.column_names = "year month "
        cls.column_names += ' '.join(cls.model.get_summary_columns())



from lino_xl.lib.cal.models import Day, Days

class Day(Day):
    def __init__(self, *args, **kwargs):
        super(Day, self).__init__(*args, **kwargs)
        self.sar = self.ar.spawn(rt.models.working.MySessionsByDay, master_instance=self)
        load_sessions(self, self.sar)

class DayDetail(dd.DetailLayout):
    main = "working.MySessionsByDay"
    # main = "working.MySessionsByDay cal.PlannerByDay"


class WorkedHours(Days, dd.VentilatingTable):
    label = _("Worked hours")
    # column_names_template = 'day_number long_date detail_link description {vcolumns}'
    column_names_template = 'detail_link worked_tickets {vcolumns} *'
    # reverse_sort_order = True
    model = Day
    detail_layout = DayDetail()

    params_layout = "user start_date end_date"
    # navigation_mode = "week"

    # parameters = Sessions.parameters
    # params_layout = Sessions.params_layout
    # use_detail_param_panel = True
    # params_panel_hidden = False

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        lst = list(super(WorkedHours, cls).get_request_queryset(ar, **filter))
        return list(reversed(lst))

    @dd.displayfield(_("Worked tickets"))
    def worked_tickets(self, obj, ar):
        # pv = dict(start_date=obj.day, end_date=obj.day)
        # pv.update(observed_event=dd.PeriodEvents.active)
        # pv.update(user=ar.param_values.user)
        # sar = ar.spawn(MySessionsByDate, param_values=pv)
        # elems = [obj.sar.ar2button(label=six.text_type(obj))]
        elems = []
        tickets = [
            ar.obj2html(t, "#{0}".format(t.id), title=t.summary)
            for t in obj._tickets]
        if len(tickets) > 0:
            # elems.append(" (")
            elems += join_elems(tickets, ', ')
            # elems.append(")")
        return E.span(*elems)

    # @dd.displayfield("Date")
    # def date(cls, row, ar):
    #     return dd.fdl(row.day)

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(WorkedHours, cls).param_defaults(ar, **kw)
        kw.update(start_date=dd.today(-6))
        kw.update(end_date=dd.today())
        kw.update(user=ar.get_user())
        return kw

    @classmethod
    def get_ventilated_columns(cls):

        def w(rpttype, verbose_name):
            def func(fld, obj, ar):
                return obj._root2tot.get(rpttype, None)

            return dd.VirtualField(dd.DurationField(verbose_name), func)

        for rpttype in ReportingTypes.objects():
            yield w(rpttype, six.text_type(rpttype))
        # yield w(None, _("N/A"))
        yield w(TOTAL_KEY, _("Total"))


    # @dd.displayfield(_("Description"))
    # def detail_link(cls, obj, ar):
    #     if ar is None:
    #         return ''
    #         # return str(self)
    #     sar = ar.spawn(cls.detail_action)
    #     sar.param_values = ar.param_values
    #     return E.div(settings.SITE.kernel.default_renderer.ar2button(sar, obj ,str(obj), style="", icon_name=None))