# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Installs standard values for :mod:`lino_xl.lib.cal`, including a
demo set of holidays.  (TODO: make them more configurable.)

See also :ref:`xl.specs.holidays`.

"""

from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta
ONE_DAY = relativedelta(days=1)
from dateutil.easter import easter

from django.conf import settings

from lino.utils.instantiator import Instantiator
from lino_xl.lib.cal.choicelists import DurationUnits, Recurrencies, WORKDAYS

from lino.api import dd, rt, _


def objects():
    cal = rt.modules.cal
    add = Instantiator('cal.Priority', 'ref').build
    yield add('1', **dd.babel_values('name', en=u"very urgent", de=u"sehr dringend",   fr=u"très urgent", et=u"väga kiire"))
    yield add('3', **dd.babel_values('name', en=u"urgent", de=u"dringend",   fr=u"urgent", et="kiire"))
    yield add('5', **dd.babel_values('name', en=u"normal", de=u"normal",   fr=u"normal", et="keskmine"))
    yield add('9', **dd.babel_values('name', en=u"not urgent", de=u"nicht dringend",   fr=u"pas urgent", et="mitte kiire"))

    calendar = Instantiator('cal.Calendar').build
    general = calendar(**dd.str2kw('name', _("General")))
    yield general
    # settings.SITE.site_config.site_calendar = general
    settings.SITE.site_config.update(
        site_calendar=general,
        hide_events_before=dd.demo_date(-300).replace(month=4, day=1))
    
    
    # yield settings.SITE.site_config

    event_type = Instantiator('cal.EventType').build
    holidays = event_type(
        is_appointment=False,
        all_rooms=True, **dd.str2kw('name', _("Holidays")))
    yield holidays
    meeting = event_type(**dd.str2kw('name', _("Meeting")))
    yield meeting    

    RecurrentEvent = rt.modules.cal.RecurrentEvent
    add = Instantiator(RecurrentEvent, event_type=holidays).build

    def holiday(month, day, en, de, fr, et=None):
        if et is None:
            et = en
        return add(
            every_unit=Recurrencies.yearly,
            monday=True, tuesday=True, wednesday=True, thursday=True,
            friday=True, saturday=True, sunday=True,
            every=1,
            start_date=datetime.date(
                year=cal.DEMO_START_YEAR,
                month=month, day=day),
            **dd.babelkw('name', en=en, de=de, fr=fr, et=et))
    yield holiday(1, 1, "New Year's Day", "Neujahr", "Jour de l'an", "Uusaasta")
    yield holiday(5, 1, "International Workers' Day", "Tag der Arbeit", "Premier Mai", "kevadpüha")
    yield holiday(7, 21, "National Day", "Nationalfeiertag", "Fête nationale", "Belgia riigipüha")
    yield holiday(8, 15, "Assumption of Mary", "Mariä Himmelfahrt", "Assomption de Marie")
    yield holiday(10, 31, "All Souls' Day", "Allerseelen", "Commémoration des fidèles défunts")
    yield holiday(11, 1, "All Saints' Day", "Allerheiligen", "Toussaint")
    yield holiday(11, 11, "Armistice with Germany", "Waffenstillstand", "Armistice")
    yield holiday(12, 25, "Christmas", "Weihnachten", "Noël", "Esimene Jõulupüha")

    easter1 = easter(cal.DEMO_START_YEAR)

    def relative_holiday(offset, name):
        return add(
            every_unit=Recurrencies.easter, every=1,
            start_date=easter1+relativedelta(days=offset),
            **dd.str2kw('name', name))

    yield relative_holiday(0, _("Easter sunday"))
    yield relative_holiday(1, _("Easter monday"))
    yield relative_holiday(39, _("Ascension of Jesus"))
    yield relative_holiday(50, _("Pentecost"))
    yield relative_holiday(-2, _("Good Friday"))
    yield relative_holiday(-46, _("Ash Wednesday"))
    yield relative_holiday(-48, _("Rosenmontag"))

    ar = settings.SITE.login()
    for obj in RecurrentEvent.objects.all():
        if not obj.update_reminders(ar):
            raise Exception("Oops, %s generated no events" % obj)


    # event policies

    kw = dict()
    for wd in WORKDAYS:
        kw[wd.name] = True
    kw.update(event_type=meeting)
    exam_policy = Instantiator(
        'cal.EventPolicy', 'every',
        every_unit=DurationUnits.months, **kw).build
    yield exam_policy(
        1, start_time="9:00",
        **dd.str2kw('name', _("Every month")))
    yield exam_policy(
        2, start_time="9:00",
        **dd.str2kw('name', _("Every 2 months")))
    yield exam_policy(
        3, **dd.str2kw('name', _("Every 3 months")))

    exam_policy = Instantiator(
        'cal.EventPolicy', 'every',
        every_unit=DurationUnits.weeks, **kw).build
    yield exam_policy(
        2, start_time="9:00",
        **dd.str2kw('name', _("Every 2 weeks")))

    exam_policy = Instantiator(
        'cal.EventPolicy', 'every',
        every_unit=DurationUnits.days, **kw).build
    yield exam_policy(
        10, max_events=1, start_time="9:00",
        **dd.str2kw('name', _("Once after 10 days")))

    exam_policy = Instantiator('cal.EventPolicy').build
    yield exam_policy(**dd.str2kw('name', _("Other")))

        
