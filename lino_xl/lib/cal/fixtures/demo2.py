# -*- coding: UTF-8 -*-
# Copyright 2011-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging ; logger = logging.getLogger(__name__)

import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings

from lino.modlib.office.roles import OfficeUser
from lino.utils import Cycler
from lino.utils import ONE_DAY
from lino.api import dd, rt, _

DEMO_DURATION = relativedelta(hours=1, minutes=30)

cal = dd.resolve_app('cal')
Event = dd.resolve_model('cal.Event')
EventType = dd.resolve_model('cal.EventType')
# Subscription = rt.models.cal.Subscription
Calendar = dd.resolve_model('cal.Calendar')

PAST_STATES = Cycler(cal.EntryStates.filter(fixed=True))
FUTURE_STATES = Cycler(cal.EntryStates.filter(fixed=False))

def pop_state(date):
    if date <= dd.demo_date():
        return PAST_STATES.pop()
    else:
        return FUTURE_STATES.pop()

# def subscribe_all():

#     for u in settings.SITE.user_model.objects.exclude(user_type=''):
#         for obj in Calendar.objects.all():
#             obj = Subscription(user=u, calendar=obj)
#             yield obj


def objects():

    #~ if settings.SITE.project_model:
        #~ PROJECTS = Cycler(settings.SITE.project_model.objects.all())
    # ETYPES = Cycler(EventType.objects.filter(is_appointment=True, fill_presences=True))
    qs = EventType.objects.filter(is_appointment=True).exclude(**dd.str2kw('name', _("Absences")))
    ETYPES = Cycler(qs)

    def s2duration(s):
        h, m = map(int, s.split(':'))
        #~ return relativedelta(hours=h,minutes=m)
        return datetime.timedelta(hours=h, minutes=m)

    def s2time(s):
        h, m = map(int, s.split(':'))
        return datetime.time(h, m)
    cal_users = [ut for ut in rt.models.users.UserTypes.get_list_items()
        if ut.has_required_roles([OfficeUser])]
    USERS = Cycler(settings.SITE.user_model.objects.exclude(email='').filter(
        user_type__in=cal_users))
    TIMES = Cycler([s2time(s)
                   for s in ('08:30', '09:40', '10:20', '11:10', '13:30')])
    #~ DURATIONS = Cycler([s2duration(s) for s in ('00:30','00:40','1:00','1:30','2:00','3:00')])
    DURATIONS = Cycler([
        s2duration(s) for s in (
            '01:00', '01:15', '1:30', '1:45', '2:00', '2:30', '3:00')])
    ACL = Cycler(cal.AccessClasses.items())
    SUMMARIES = Cycler((
        dict(en='Lunch', de=u"Mittagessen", fr=u"Diner"),
        dict(en='Dinner', de=u"Abendessen", fr=u"Souper"),
        dict(en='Breakfast', de=u"Frühstück", fr=u"Petit-déjeuner"),
        dict(en='Meeting', de=u"Treffen", fr=u"Rencontre"),
        dict(en='Consultation', de=u"Beratung", fr=u"Consultation"),
        dict(en='Seminar', de=u"Seminar", fr=u"Séminaire"),
        dict(en='Evaluation', de=u"Auswertung", fr=u"Evaluation"),
        dict(en='First meeting', de=u"Erstgespräch", fr=u"Première rencontre"),
        dict(en='Interview', de=u"Interview", fr=u"Interview")
    ))

    date = settings.SITE.demo_date(-20)
    for i in range(60):
        u = USERS.pop()
        if i % 3:
            date += ONE_DAY  # relativedelta(days=1)
        s = SUMMARIES.pop().get(
            u.language, None) or SUMMARIES.pop().get('en')
        st = TIMES.pop()
        kw = dict(user=u,
                  start_date=date,
                  event_type=ETYPES.pop(),
                  start_time=st,
                  summary=s)
        kw.update(access_class=ACL.pop())
        kw.update(state=pop_state(date))

        #~ if settings.SITE.project_model:
            #~ kw.update(project=PROJECTS.pop())
        e = Event(**kw)
        e.set_datetime('end', e.get_datetime('start')
                       + DURATIONS.pop())
        yield e

    if dd.plugins.cal.demo_absences:
        absence = EventType.objects.get(**dd.str2kw('name', _("Absences")))
        date = settings.SITE.demo_date(-2)
        s = _("Absent for private reasons")
        for i in range(10):
            u = USERS.pop()
            date += ONE_DAY
            kw = dict(user=u,
                      start_date=date,
                      end_date=date + datetime.timedelta(days=(i%3)+1),
                      event_type=absence,
                      summary=s)
            kw.update(state=pop_state(date))
            yield Event(**kw)


    # # some conflicting events
    # USERS = Cycler(rt.users.User.objects.all())
    # ET = EventType.objects.filter(is_appointment=True)
    # date = settings.SITE.demo_date(200)
    # e = Event(start_date=date, summary="Conflicting 1", event_type=ETYPES.pop(), user=USERS.pop())
    # yield e
