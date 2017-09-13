# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)

import sys


from django.conf import settings
from django.db.models import Count

from lino.api import dd, rt, _

from lino.utils import ONE_DAY
from lino.utils.xmlgen.html import E, join_elems
from lino.utils.quantities import Duration
from lino.modlib.system.choicelists import ObservedEvent
from lino.mixins.periods import ObservedDateRange
from django.contrib.humanize.templatetags.humanize import naturaltime
from datetime import datetime

from lino_xl.lib.tickets.choicelists import (
    TicketEvents, ProjectEvents, ObservedEvent)

from .roles import Worker

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

TicketEvents.add_item_instance(TicketHasSessions("clocking"))


class ProjectHasSessions(ObservedEvent):
    text = _("Has been worked on")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(
                tickets_by_project__sessions_by_ticket__start_date__gte=
                pv.start_date)
        if pv.end_date:
            qs = qs.filter(
                tickets_by_project__sessions_by_ticket__end_date__lte=
                pv.end_date)
        qs = qs.annotate(num_sessions=Count(
            'tickets_by_project__sessions_by_ticket'))
        qs = qs.filter(num_sessions__gt=0)
        return qs

ProjectEvents.add_item_instance(ProjectHasSessions("clocking"))


class SessionTypes(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = 'clocking.SessionType'
    column_names = 'name *'


class Sessions(dd.Table):
    required_roles = dd.login_required(Worker)
    model = 'clocking.Session'
    column_names = 'ticket user start_date start_time end_date end_time '\
                   'break_time summary duration ticket_no  *'

    detail_layout = """
    ticket:40 user:20 faculty:20
    start_date start_time end_date end_time break_time duration
    summary:60 workflow_buttons:20
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
        project=dd.ForeignKey(
            'tickets.Project', null=True, blank=True),
        ticket=dd.ForeignKey(
            dd.plugins.clocking.ticket_model, null=True, blank=True),
        # user=dd.ForeignKey('users.User', null=True, blank=True),
        session_type=dd.ForeignKey(
            'clocking.SessionType', null=True, blank=True),
        observed_event=dd.PeriodEvents.field(
            blank=True, default=dd.PeriodEvents.active.as_callable),
    )

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(Sessions, cls).get_simple_parameters())
        s += ['session_type', 'ticket']
        return s

    params_layout = "start_date end_date observed_event company project "\
                    "user session_type ticket"
    auto_fit_column_widths = True

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Sessions, self).get_request_queryset(ar)
        pv = ar.param_values
        ce = pv.observed_event
        if ce is not None:
            qs = ce.add_filter(qs, pv)

        if pv.project:
            qs = qs.filter(ticket__project__in=pv.project.whole_clan())

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
                   'break_time duration user *'
    slave_grid_format = 'summary'

    @classmethod
    def get_slave_summary(self, obj, ar):
        if ar is None:
            return ''
        elems = []

        # Button for starting a session from ticket
        sar = obj.start_session.request_from(ar)
        # if ar.renderer.is_interactive and sar.get_permission():
        if sar.get_permission():
            btn = sar.ar2button(obj)
            elems += [E.p(btn)]

        # Active sessions:
        active_sessions = []
        session_summaries = E.ul()
        qs = rt.modules.clocking.Session.objects.filter(ticket=obj)
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
        'start_time end_time break_time duration summary ticket '
        'workflow_buttons *')

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


