# -*- coding: UTF-8 -*-
# Copyright 2011-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals


from django.conf import settings
from django.db import models
from django.utils import timezone

from lino import mixins
from lino.api import dd, rt, _, gettext

from etgen.html import E
from lino.utils.quantities import Duration
from lino.mixins.periods import DateRange
from lino.modlib.users.mixins import UserAuthored
from lino.modlib.summaries.mixins import MonthlySlaveSummary
from lino.modlib.about.choicelists import TimeZones

from lino_xl.lib.cal.mixins import Started, Ended
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.tickets.choicelists import TicketStates

from .actions import EndThisSession, PrintActivityReport, EndTicketSession, ShowMySessionsByDay
from .choicelists import ReportingTypes, ZERO_DURATION
from .mixins import Workable


class SessionType(mixins.BabelNamed):

    class Meta:
        app_label = 'working'
        verbose_name = _("Session Type")
        verbose_name_plural = _('Session Types')


# class Location(mixins.BabelDesignated):

#     class Meta:
#         app_label = 'working'
#         verbose_name = _("Location")
#         verbose_name_plural = _('Locations')

#     time_zone = dd.ForeignKey(
#         dd.plugins.working.ticket_model,
#         related_name="sessions_by_ticket")


@dd.python_2_unicode_compatible
class Session(UserAuthored, Started, Ended, Workable):
    class Meta:
        app_label = 'working'
        verbose_name = _("Session")
        verbose_name_plural = _('Sessions')
        abstract = dd.is_abstract_model(__name__, 'Session')

    ticket = dd.ForeignKey(
        dd.plugins.working.ticket_model,
        related_name="sessions_by_ticket")

    session_type = dd.ForeignKey(
        'working.SessionType', null=True, blank=True)
    summary = models.CharField(
        _("Summary"), max_length=200, blank=True,
        help_text=_("Summary of the session."))
    description = dd.RichTextField(_("Description"), blank=True)
    # break_time = models.TimeField(
    #     blank=True, null=True,
    #     verbose_name=_("Break Time"))
    break_time = dd.DurationField(_("Break Time"), blank=True, null=True)
    faculty = dd.ForeignKey(
        'skills.Skill', related_name="sessions_by_faculty",
        blank=True, null=True)

    reporting_type = ReportingTypes.field(blank=True)
    is_fixing = models.BooleanField(_("Fixing"), default=False)
    if settings.USE_TZ:
        time_zone = TimeZones.field()
    else:
        time_zone = dd.DummyField()
    
    end_session = EndThisSession()
    show_today = ShowMySessionsByDay('start_date')
    # print_activity_report = PrintActivityReport()

    def __str__(self):
        if self.start_time and self.end_time:
            return u"%s %s-%s" % (
                self.start_date.strftime(settings.SITE.date_format_strftime),
                self.start_time.strftime(settings.SITE.time_format_strftime),
                self.end_time.strftime(settings.SITE.time_format_strftime))
        return "%s # %s" % (self._meta.verbose_name, self.pk)

    def get_ticket(self):
        return self.ticket
    
    def on_create(self, ar):
        super(Session, self).on_create(ar)
        if settings.USE_TZ:
            self.time_zone = self.user.time_zone or \
                             rt.models.about.TimeZones.default
        
    def get_time_zone(self):
        return self.time_zone
    
    def full_clean(self, *args, **kwargs):
        if self.user_id and not self.time_zone:
            # can be removed when all production sites have migrated:
            self.time_zone = self.user.time_zone or \
                             rt.models.about.TimeZones.default
            
        if not settings.SITE.loading_from_dump:
            if self.start_time is None:
                self.set_datetime('start', timezone.now())
                # value = timezone.now()
                # if pytz:
                #     tz = pytz.timezone(self.get_timezone())
                #     value = value.astimezone(tz)
                # self.start_time = value.time()
            if self.start_date is None:
                self.start_date = dd.today()
            # if self.ticket_id is not None and self.faculty_id is None:
            #     self.faculty = self.ticket.faculty
            if self.end_time is not None:
                if self.end_date is None:
                    self.end_date = self.start_date
            if self.ticket_id:
                self.ticket.on_worked(self)
                    
        super(Session, self).full_clean(*args, **kwargs)

    def unused_save(self, *args, **kwargs):
        if not settings.SITE.loading_from_dump:
            if self.start_date is None:
                self.start_date = dd.today()
            if self.start_time is None:
                self.start_time = timezone.now().time()
        super(Session, self).save(*args, **kwargs)

    def get_reporting_type(self):
        if self.reporting_type:
            return self.reporting_type
        t = self.get_ticket()
        if t.ticket_type and t.ticket_type.reporting_type:
            return t.ticket_type.reporting_type
        if t.site and t.site.reporting_type:
            return t.site.reporting_type
        # if t.project and t.project.reporting_type:
        #     return t.project.reporting_type
        return dd.plugins.working.default_reporting_type

    # def after_ui_save(self, ar, cw):
    #     super(Session, self).after_ui_save(ar, cw)
    #     if self.ticket_id:
    #         self.ticket.on_worked(self, ar, cw)
        
    def get_root_project(self):
        """Return the root project for this session (or None if session has no
        ticket).

        """
        if self.ticket and self.ticket.project:
            return self.ticket.project.get_parental_line()[0]

    def get_duration(self):
        """Return the duration in hours as a
        :class:`lino.utils.quantities.Quantity`.  This inherits from
        :meth:`StartedEnded
        <lino_xl.lib.cal.mixins.StartedEnded.get_duration>` but
        removes :attr:`break_time` if specified.

        """
        diff = super(Session, self).get_duration()
        if diff and self.break_time:
            diff -= self.break_time
        return diff
        
        # if self.end_time is None:
        #     diff = datetime.timedelta()
        # else:
        #     diff = self.get_datetime('end') - self.get_datetime('start')
        #     if self.break_time is not None:
        #         diff -= self.break_time
        # return Duration(diff)

    @dd.displayfield(_("Ticket #"))
    def ticket_no(self, ar):
        if ar is None:
            return self.ticket_id
        return self.ticket.obj2href(ar)  # self.ticket_id)

    @dd.displayfield(_("Site"))
    def site_ref(self, ar):
        if not self.ticket:
            return ''
        site = self.ticket.site
        if site is None:
            return ''
        if ar is None:
            return str(site)
        return site.obj2href(ar)

dd.update_field(
    Session, 'user', blank=False, null=False, verbose_name=_("Worker"))
dd.update_field(
    Session, 'end_time', db_index=True)

Session.set_widget_options('ticket__id', label=_("Ticket #"))
Session.set_widget_options('ticket_no', width=8)
Session.set_widget_options('break_time', hide_sum=True)


@dd.python_2_unicode_compatible
class ServiceReport(UserAuthored, ContactRelated, Certifiable, DateRange):
    class Meta:
        app_label = 'working'
        verbose_name = _("Service Report")
        verbose_name_plural = _("Service Reports")

    interesting_for = dd.ForeignKey(
        'contacts.Partner',
        verbose_name=_("Interesting for"),
        blank=True, null=True,
        help_text=_("Only tickets interesting for this partner."))

    ticket_state = TicketStates.field(
        null=True, blank=True,
        help_text=_("Only tickets in this state."))

    def __str__(self):
        return "{} {}".format(self._meta.verbose_name, self.pk)

    def get_tickets_parameters(self, **pv):
        """Return a dict with parameter values for `tickets.Tickets` based on
        the options of this report.

        """
        pv.update(start_date=self.start_date, end_date=self.end_date)
        pv.update(interesting_for=self.interesting_for)
        if self.ticket_state:
            pv.update(state=self.ticket_state)
        return pv

dd.update_field(ServiceReport, 'user', verbose_name=_("Worker"))


class SummaryBySession(MonthlySlaveSummary):
    # common base for UserSummary and SiteSummary

    class Meta:
        abstract = True

    @classmethod
    def get_summary_columns(cls):
        for t in ReportingTypes.get_list_items():
            k = t.name + '_hours'
            yield k

    def reset_summary_data(self):
        for t in ReportingTypes.get_list_items():
            k = t.name + '_hours'
            setattr(self, k, ZERO_DURATION)

    def add_from_session(self, obj):
        d = obj.get_duration()
        if d:
            rt = obj.get_reporting_type()
            k = rt.name + '_hours'
            value = getattr(self, k) + d
            setattr(self, k, value)


class UserSummary(SummaryBySession):

    class Meta:
        app_label = 'working'
        verbose_name = _("User summary")
        verbose_name_plural = _("User summaries")

    summary_period = 'monthly'
    delete_them_all = True
    master = dd.ForeignKey('users.User')

    def get_summary_collectors(self):
        qs = rt.models.working.Session.objects.filter(
            user=self.master)
        if self.year:
            qs = qs.filter(
                start_date__year=self.year)
        if self.month:
            qs = qs.filter(
                start_date__month=self.month)
        yield (self.add_from_session, qs)


class SiteSummary(SummaryBySession):

    class Meta:
        app_label = 'working'
        verbose_name = _("Site summary")
        verbose_name_plural = _("Site summaries")

    summary_period = 'yearly'
    delete_them_all = True
    master = dd.ForeignKey('tickets.Site')

    active_tickets = models.IntegerField(_("Active tickets"))
    inactive_tickets = models.IntegerField(_("Inactive tickets"))

    # @classmethod
    # def get_summary_master_model(cls):
    #     return rt.models.tickets.Site

    # @classmethod
    # def get_summary_masters(cls):
    #     return rt.models.tickets.Site.objects.order_by('id')

    @classmethod
    def get_summary_columns(cls):
        for k in super(SiteSummary, cls).get_summary_columns():
            yield k
        yield 'active_tickets'
        yield 'inactive_tickets'


    def reset_summary_data(self):
        super(SiteSummary, self).reset_summary_data()
        # for ts in TicketStates.get_list_items():
        #     k = ts.get_summary_field()
        #     if k is not None:
        #         setattr(self, k, 0)
        self.active_tickets = 0
        self.inactive_tickets = 0
            
    def get_summary_collectors(self):
        if self.year is None:
            qs = rt.models.tickets.Ticket.objects.filter(site=self.master)
            # qs = qs.filter(
            #     sessions_by_ticket__start_date__year=self.year)
            yield (self.add_from_ticket, qs)

        qs = rt.models.working.Session.objects.filter(
            ticket__site=self.master)
        if self.year:
            qs = qs.filter(
                start_date__year=self.year)
        yield (self.add_from_session, qs)
    
    def add_from_ticket(self, obj):
        ts = obj.state
        # k = ts.get_summary_field()
        # if k is not None:
        #     value = getattr(self, k) + 1
        #     setattr(self, k, value)
        if ts.active:
            self.active_tickets += 1
        else:
            self.inactive_tickets += 1



@dd.receiver(dd.pre_analyze)
def inject_summary_fields(sender, **kw):
    SiteSummary = rt.models.working.SiteSummary
    UserSummary = rt.models.working.UserSummary
    WorkSite = rt.models.tickets.Site
    Ticket = dd.plugins.working.ticket_model
    for t in ReportingTypes.get_list_items():
        k = t.name + '_hours'
        dd.inject_field(
            SiteSummary, k, dd.DurationField(t.text, null=True, blank=True))
        dd.inject_field(
            UserSummary, k, dd.DurationField(t.text, null=True, blank=True))
        dd.inject_field(
            Ticket, k, dd.DurationField(t.text, null=True, blank=True))

        def make_getter(t):
            k = t.name + '_hours'
            def getter(obj, ar):
                qs = SiteSummary.objects.filter(
                    master=obj, year__isnull=True)
                d = qs.aggregate(**{k:models.Sum(k)})
                n = d[k]
                return n
            return getter

        dd.inject_field(
            WorkSite, k, dd.VirtualField(
                dd.DurationField(t.text), make_getter(t)))


    if False:  # removed 20181211 because useless
      for ts in TicketStates.get_list_items():
        k = ts.get_summary_field()
        if k is not None:
            dd.inject_field(
                SiteSummary, k, models.IntegerField(ts.text))

            def make_getter(ts):
                k = ts.get_summary_field()
                def getter(obj, ar):
                    if ar is None:
                        return ''
                    qs = SiteSummary.objects.filter(master=obj)
                    d = qs.aggregate(**{k:models.Sum(k)})
                    n = d[k]
                    if n == 0:
                        return ''
                    sar = rt.models.tickets.TicketsBySite.request(
                        obj, param_values=dict(
                            state=ts, show_active=None))
                    # n = sar.get_total_count()
                    url = ar.renderer.request_handler(sar)
                    if url is None:
                        return str(n)
                    return E.a(str(n), href='javascript:'+url)
                return getter

            dd.inject_field(
                WorkSite, k, dd.VirtualField(
                    dd.DisplayField(ts.text), make_getter(ts)))



def welcome_messages(ar):
    """Yield messages for the welcome page."""
    #todo show all users active sessions

    Session = rt.models.working.Session
    # Ticket = rt.models.tickets.Ticket
    # TicketStates = rt.models.tickets.TicketStates
    me = ar.get_user()

    # your open sessions (i.e. those you are busy with)
    qs = Session.objects.filter(end_time__isnull=True)
    working = {me:[E.b(six.text_type(_("You are busy with ")))]}
    if qs.count() == 0:
        return
    for ses in qs:
        if ses.user not in working:
            working[ses.user] = [ar.obj2html(ses.user),
                                 gettext(" is working on: ")]
        txt = six.text_type(ses.ticket)
        working[ses.user].append(
            ar.obj2html(ses.ticket, txt, title=getattr(ses.ticket,'summary',"") or
                                               getattr(ses.ticket,'name',"")))

        if ses.user == me:
            working[ses.user] += [
                ' (',
                ar.instance_action_button(
                    ses.end_session, EndTicketSession.label),
                ')']
        working[ses.user].append(', ')

    if len(working[me]) > 1:

        working[me][-1] = working[me][-1].replace(", ", ".")
        result = E.p(*working.pop(me))
    else:
        result = E.p()
        working.pop(me)
    for u, s in working.items():
        if len(result):
            result.append(E.br())
        s[-1] = s[-1].replace(", ", ".")
        result.append(E.span(*s))
    yield result

dd.add_welcome_handler(welcome_messages)


if False:  # works, but is not useful

    def weekly_reporter(days, ar, start_date, end_date):
        Session = rt.models.working.Session
        me = ar.get_user()
        qs = Session.objects.filter(
            user=me, start_date__gte=start_date, end_date__lte=end_date)
        # print 20150420, start_date, end_date, qs
        d2p = dict()
        for ses in qs:
            prj = ses.ticket.project
            if prj is not None:
                while prj.parent is not None:
                    prj = prj.parent
            projects = d2p.setdefault(ses.start_date, dict())
            duration = projects.setdefault(prj, Duration())
            duration += ses.get_duration()
            projects[prj] = duration

        # print 20150420, d2p
        def fmt(delta):
            return str(Duration(delta))

        for date, projects in d2p.items():
            parts = []
            tot = Duration()
            for prj, duration in projects.items():
                if prj is None:
                    prj = "N/A"
                txt = "{0} ({1})".format(prj, fmt(duration))
                parts.append(txt)
                tot += duration
            if len(parts):
                if len(parts) == 1:
                    txt = parts[0]
                else:
                    txt = ', '.join(parts) + " = " + fmt(tot)
                txt = E.p(txt, style="text-align:right")
                days[date].append(txt)

    from lino.utils.weekly import add_reporter
    add_reporter(weekly_reporter)


from lino.modlib.checkdata.choicelists import Checker
class TicketSessionsChecker(Checker):
    """

    """
    model = dd.plugins.working.ticket_model
    verbose_name = _("Check the fixed_since field of tickets.")

    def get_checkdata_problems(self, obj, fix=False):
        qs = rt.models.working.Session.objects.filter(
            ticket=obj, end_time__isnull=False, is_fixing=True)
        qs = qs.order_by('end_date', 'end_time')
        ses = qs.first()
        if ses is None:
            if obj.fixed_since is not None:
                if fix:
                    obj.fixed_since = None
                    obj.full_clean()
                    obj.save()
                yield (True, _("No fixing session but marked as fixed"))
        else:
            if obj.fixed_since is None:
                if fix:
                    obj.fixed_since = ses.get_datetime('end')
                    obj.full_clean()
                    obj.save()
                yield (True, _(
                    "Fixing session exists but ticket not marked as fixed"))

TicketSessionsChecker.activate()
    

# dd.inject_field(
#     'tickets.Project',
#     'reporting_type', ReportingTypes.field(blank=True))

dd.inject_field(
    "users.User", 'open_session_on_new_ticket',
    models.BooleanField(_("Open session on new ticket"), default=False))


from .ui import *
