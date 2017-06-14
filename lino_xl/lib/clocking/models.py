# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Database models for this plugin.

"""

# import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from lino import mixins
from lino.api import dd, rt, _

from lino.utils.xmlgen.html import E
from lino.utils.quantities import Duration

from lino_xl.lib.cal.mixins import Started, Ended
from lino.modlib.users.mixins import UserAuthored

from .actions import EndThisSession, PrintActivityReport, EndTicketSession, ShowMySessionsByDay
from .choicelists import ReportingTypes
from .mixins import Workable


class SessionType(mixins.BabelNamed):
    """The type of a :class:`Session`.
    """

    class Meta:
        app_label = 'clocking'
        verbose_name = _("Session Type")
        verbose_name_plural = _('Session Types')


@dd.python_2_unicode_compatible
class Session(UserAuthored, Started, Ended, Workable):
    """A **Session** is when a user works during a given lapse of time on
    a given Ticket.

    Extreme case of a session:

    - I start to work on an existing ticket #1 at 9:23.  A customer phones
      at 10:17 with a question. Created #2.  That call is interrupted
      several times (by the customer himself).  During the first
      interruption another customer calls, with another problem (ticket
      #3) which we solve together within 5 minutes.  During the second
      interruption of #2 (which lasts 7 minutes) I make a coffee break.

      During the third interruption I continue to analyze the
      customer's problem.  When ticket #2 is solved, I decided that
      it's not worth to keep track of each interruption and that the
      overall session time for this ticket can be estimated to 0:40.

      ::

        Ticket start end    Pause  Duration
        #1      9:23 13:12  0:45
        #2     10:17 11:12  0:12       0:43
        #3     10:23 10:28             0:05


    .. attribute:: start_date

        The date when you started to work.

    .. attribute:: start_time

        The time (in `hh:mm`) when you started working on this
        session.

        This is your local time according to the time zone specified
        in your preferences.

    .. attribute:: end_date

        Leave this field blank if it is the same date as start_date.

    .. attribute:: end_time

        The time (in `hh:mm`) when you stopped to work. This is empty
        as long as you are busy with this session.

    .. attribute:: break_time
    
       The time (in `hh:mm`) to remove from the duration resulting
       from the difference between :attr:`start_time` and
       :attr:`end_time`.

    .. attribute:: faculty

       The faculty that has been used during this session. On a new
       session this defaults to the needed faculty currently specified
       on the ticket.

    """
    class Meta:
        app_label = 'clocking'
        verbose_name = _("Session")
        verbose_name_plural = _('Sessions')
        abstract = dd.is_abstract_model(__name__, 'Session')

    ticket = dd.ForeignKey(
        dd.plugins.clocking.ticket_model,
        related_name="sessions_by_ticket")

    session_type = dd.ForeignKey(
        'clocking.SessionType', null=True, blank=True)
    summary = models.CharField(
        _("Summary"), max_length=200, blank=True,
        help_text=_("Summary of the session."))
    description = dd.RichTextField(_("Description"), blank=True)
    # break_time = models.TimeField(
    #     blank=True, null=True,
    #     verbose_name=_("Break Time"))
    break_time = dd.DurationField(_("Break Time"), blank=True, null=True)
    faculty = dd.ForeignKey(
        'faculties.Faculty', related_name="sessions_by_faculty",
        blank=True, null=True)

    reporting_type = ReportingTypes.field(blank=True)
    
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
    
    def full_clean(self, *args, **kwargs):
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
        if self.ticket and self.ticket.project:
            if self.ticket.project.reporting_type:
                return self.ticket.project.reporting_type
        return dd.plugins.clocking.default_reporting_type

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

dd.update_field(
    Session, 'user', blank=False, null=False, verbose_name=_("Worker"))

Session.set_widget_options('ticket__id', label=_("Ticket #"))
Session.set_widget_options('ticket_no', width=8)


def welcome_messages(ar):
    """Yield messages for the welcome page."""
    #todo show all users active sessions

    Session = rt.modules.clocking.Session
    # Ticket = rt.modules.tickets.Ticket
    # TicketStates = rt.modules.tickets.TicketStates
    me = ar.get_user()

    # your open sessions (i.e. those you are busy with)
    qs = Session.objects.filter(end_time__isnull=True)
    working = {me:[E.b(unicode(_("You are busy with ")))]}
    if qs.count() > 0:
        for ses in qs:
            if ses.user not in working:
                working[ses.user] = [ar.obj2html(ses.user), _(" is working on: ")]
            txt = unicode(ses.ticket)
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
        Session = rt.modules.clocking.Session
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

# dd.inject_field(
#     'tickets.Project',
#     'reporting_type', ReportingTypes.field(blank=True))

dd.inject_field(
    "users.User", 'open_session_on_new_ticket',
    models.BooleanField(_("Open session on new ticket"), default=False))


from .ui import *
