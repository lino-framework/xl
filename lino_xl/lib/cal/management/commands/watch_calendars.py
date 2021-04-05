# -*- coding: UTF-8 -*-
# Copyright 2011-2013 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Starts a daemon (or, if daemons are not supported, a nomal console process)
that watches for changes in remote calendars.
See also :srcref:`docs/tickets/47`

"""

import os
import sys
import codecs
import time
import datetime
#~ import signal
import atexit
from cStringIO import StringIO

import vobject
try:
    import caldav
    from caldav.elements import dav, cdav
except ImportError:
    pass  # the command won't work, but at least sphinx autodoc will

#~ from lino_xl.lib.cal.models import Calendar, Event
from vobject.icalendar import VEvent, RecurringComponent


from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError


from django.conf import settings


from django.db.utils import DatabaseError
from django.db import models

import lino

from lino.api import dd, rt

from lino.utils import confirm, iif
from lino.utils import dblogger

from lino.utils.daemoncommand import DaemonCommand
from ...utils import aware, dt2kw, setkw


Place = dd.resolve_model('cal.Place')
Calendar = dd.resolve_model('cal.Calendar')
Event = dd.resolve_model('cal.Event')
RecurrenceSet = dd.resolve_model('cal.RecurrenceSet')

# dblogger.log_changes(REQUEST,obj)


def prettyPrint(obj):
    s = StringIO()
    out = sys.stdout
    sys.stdout = s
    obj.prettyPrint()
    sys.stdout = out
    return s.getvalue()


def receive(dbcal, calendar):

    rs_touched = set()
    ev_touched = set()
    rs_updated = rs_created = rs_deleted = 0
    count_update = 0
    count_new = 0
    count_deleted = 0
    #~ print "Using calendar", calendar

    props = calendar.get_properties([dav.DisplayName()])
    dbcal.name = props[dav.DisplayName().tag]
    dbcal.save()

    from_date = dbcal.start_date
    if not from_date:
        from_date = datetime.datetime.now() - datetime.timedelta(days=365)
    until_date = datetime.datetime.now() + datetime.timedelta(days=365)

    #~ from_date = aware(from_date)
    #~ until_date = aware(until_date)

    #~ print from_date.tzinfo, until_date.tzinfo
    #~ raise Exception("20110823")

    results = calendar.date_search(from_date, until_date)
    if results:
        for comp in results:
            #~ if len(list(comp.instance.getChildren())) != 1:
                #~ raise Exception("comp.instance.getChildren() is %s" % list(comp.instance.getChildren()))
            dblogger.info(
                "Got calendar component <<<\n%s\n>>>",
                prettyPrint(comp.instance))

            if comp.instance.vevent:
                event = comp.instance.vevent
                if isinstance(event, RecurringComponent):
                    """
                    in a google calendar, all events are parsed to a
                    RecurringComponent. if event.rruleset is None
                    we consider them non recurrent.
                    """

                    uid = event.uid.value
                    dtstart = event.dtstart.value

                    get_kw = {}
                    set_kw = {}
                    get_kw.update(uid=uid)
                    set_kw.update(summary=event.summary.value)
                    #~ dblogger.info("TRANSPARENCE IS %r", event.transp.value)
                    location_name = event.location.value
                    if location_name:
                        qs = Place.objects.filter(name__iexact=location_name)
                        if qs.count() == 0:
                            pl = Place(name=location_name)
                            pl.full_clean()
                            pl.save()
                            dblogger.info("Auto-created location %s", pl)
                        else:
                            pl = qs[0]
                            if qs.count() > 1:
                                dblogger.warning(
                                    "Found more than 1 Place for location %r", location_name)
                        set_kw.update(place=pl)
                    else:
                        set_kw.update(place=None)
                    if event.transp.value == 'TRANSPARENT':
                        set_kw.update(transparent=True)
                    else:
                        set_kw.update(transparent=False)
                    set_kw.update(description=event.description.value)
                    set_kw.update(calendar=dbcal)
                    #~ set_kw.update(location=event.location.value)
                    #~ kw.update(dtend=event.dtend.value)

                    dblogger.info("It's a RecurringComponent")
                    if event.rruleset:
                        try:
                            obj = RecurrenceSet.objects.get(uid=uid)
                            assert obj.calendar == dbcal
                            rs_updated += 1
                        except RecurrenceSet.DoesNotExist as e:
                        #~ except Exception, e:
                            obj = RecurrenceSet(uid=uid)
                            obj.calendar = dbcal
                            obj.user = dbcal.user
                            rs_created += 1
                        #~ raise Exception("20110823 must save rrule, rdate etc... %s" % type(event.rrule_list))
                        obj.rrules = '\n'.join(
                            [r.value for r in event.rrule_list])
                        #~ obj.exrules = '\n'.join([r.value for r in event.exrule_list])
                        #~ obj.rdates = '\n'.join([r.value for r in event.rdate_list])
                        #~ obj.exdates = '\n'.join([r.value for r in event.exdate_list])
                        obj.summary = event.summary.value
                        obj.description = event.description.value
                        setkw(obj, **dt2kw(dtstart, 'start'))
                        obj.full_clean()
                        obj.save()
                        dblogger.info("Saved %s", obj)
                        rs_touched.add(obj.pk)

                        set_kw.update(rset=obj)
                        if getattr(dtstart, 'tzinfo', False):
                            dtlist = event.rruleset.between(
                                aware(from_date), aware(until_date))
                        else:
                            dtlist = event.rruleset.between(
                                from_date, until_date)
                        dblogger.info("rrulset.between() --> %s", dtlist)
                    else:
                        dtlist = [dtstart]
                        dblogger.info("No rruleset")
                    duration = event.dtend.value - dtstart
                    for dtstart in dtlist:
                        dtend = dtstart + duration
                        get_kw = dt2kw(dtstart, 'start', **get_kw)
                        set_kw = dt2kw(dtend, 'end', **set_kw)
                        try:
                            obj = Event.objects.get(**get_kw)
                            count_update += 1
                        except Event.DoesNotExist as e:
                        #~ except Exception, e:
                            obj = Event(**get_kw)
                            obj.user = dbcal.user
                            count_new += 1
                        setkw(obj, **set_kw)
                        obj.full_clean()
                        obj.save()
                        dblogger.info("Saved %s", obj)
                        ev_touched.add(obj.pk)

                else:
                    raise Exception(
                        "comp.instance.vevent is a %s (expected VEvent)" % type(event))
            else:
                raise Exception(
                    "Got unhandled component %s"
                    % comp.instance.prettyPrint())
                #~ print "children:", [c for c in comp.instance.getChildren()]

            #~ raise StopIteration
    qs = dbcal.event_set.exclude(id__in=ev_touched)
    count_deleted = qs.count()
    qs.delete()  # note: doesn't call delete methods of individual objects
    qs = dbcal.recurrenceset_set.exclude(id__in=rs_touched)
    rs_deleted = qs.count()
    qs.delete()  # note: doesn't call delete methods of individual objects
    dblogger.info(
        "--> Created %d, updated %d, deleted %s Events",
        count_new, count_update, count_deleted)
    dblogger.info(
        "--> Created %d, updated %d, deleted %s RecurrenceSets",
        rs_created, rs_updated, rs_deleted)


def send(dbcal, calendar, client):
    n = 0
    for obj in dbcal.event_set.filter(user_modified=True):
        dblogger.info("Gonna send %s", obj)
        n += 1

        mycal = vobject.iCalendar()
        #~ mycal.add('vevent')

        #~ mycal = vobject.iCalendar()
        #~ vevent = vobject.newFromBehavior('vevent', '2.0')
        vevent = mycal.add('vevent')
        vevent.add('uid').value = obj.uid
        vevent.add('dtstamp').value = obj.modified
        if obj.start_time:
            vevent.add('dtstart').value = datetime.datetime.combine(
                obj.start_date, obj.start_time)
        else:
            vevent.add('dtstart').value = obj.start_date
        if obj.end_time:
            vevent.add('dtend').value = datetime.datetime.combine(
                obj.end_date, obj.end_time)
        else:
            vevent.add('dtend').value = obj.end_date
        vevent.add('transp').value = iif(
            obj.transparent, 'TRANSPARENT', 'OPAQUE')
        vevent.add('summary').value = obj.summary
        if obj.place:
            vevent.add('location').value = obj.place.name
        vevent.add('description').value = obj.description
        event = caldav.Event(
            client, data=mycal.serialize(), parent=calendar).save()
    dblogger.info("--> Sent %d events to calendar server.", n)


def watch():
    """
    Loops through all remote calendars,
    synchronizing them with their calendar server.
    We first send local changes to the server,
    then retrieve remote changes into our database.

    Deserves more documentation.
    """
    for dbcal in Calendar.objects.filter(url_template__isnull=False):
        #~ if not dbcal.url_template:
            #~ continue
        url = dbcal.get_url()
        #~ dblogger.info("Synchronize calendar %s using %s",dbcal.name, url)
        dblogger.info("Synchronize calendar %s...", dbcal.name)

        client = caldav.DAVClient(url)
        principal = caldav.Principal(client, url)
        #~ print "url.username:", principal.url.username
        #~ print "url.hostname:", principal.url.hostname

        calendars = principal.calendars()
        if len(calendars) == 0:
            dblogger.info("--> Sorry, no calendar")
        elif len(calendars) > 1:
            #~ print "WARNING: more than 1 calendar"
            dblogger.warning("--> More than 1 calendar")
        else:
            send(dbcal, calendars[0], client)
            receive(dbcal, calendars[0])


def main(*args, **options):
    #~ msg = "Started watch_calendars %s..."
    #~ dblogger.info(msg,lino.__version__)

    #~ def goodbye():
        #~ msg = "Stopped watch_calendars %s ..."
        #~ dblogger.info(msg,lino.__version__)
    #~ atexit.register(goodbye)

    while True:
        watch()
        #~ try:
            #~ watch()
        #~ except Exception,e:
            #~ dblogger.exception(e)
        break  # temporarily while testing
        time.sleep(60)  # sleep for a minute


class Command(DaemonCommand):

    help = __doc__

    preserve_loggers = [dblogger.logger]

    def handle_daemon(self, *args, **options):
        #~ settings.SITE.startup()
        main(*args, **options)
