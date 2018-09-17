# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

import datetime
from dateutil.easter import easter

from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd, _
from lino.utils.format_date import fds

from .utils import day_and_month

class Weekdays(dd.ChoiceList):
    verbose_name = _("Weekday")
add = Weekdays.add_item
add('1', _('Monday'), 'monday')
add('2', _('Tuesday'), 'tuesday')
add('3', _('Wednesday'), 'wednesday')
add('4', _('Thursday'), 'thursday')
add('5', _('Friday'), 'friday')
add('6', _('Saturday'), 'saturday')
add('7', _('Sunday'), 'sunday')

WORKDAYS = frozenset([
    Weekdays.get_by_name(k)
    for k in 'monday tuesday wednesday thursday friday'.split()])


class DurationUnit(dd.Choice):

    def add_duration(unit, orig, value):
        if orig is None:
            return None
        if unit.value == 's':
            return orig + datetime.timedelta(seconds=value)
        if unit.value == 'm':
            return orig + datetime.timedelta(minutes=value)
        if unit.value == 'h':
            return orig + datetime.timedelta(hours=value)
        if unit.value == 'D':
            return orig + datetime.timedelta(days=value)
        if unit.value == 'W':
            return orig + datetime.timedelta(days=value * 7)
        day = orig.day
        while True:
            year = orig.year
            try:
                if unit.value == 'M':
                    m = orig.month + value
                    while m > 12:
                        m -= 12
                        year += 1
                    while m < 1:
                        m += 12
                        year -= 1
                    return orig.replace(month=m, day=day, year=year)
                if unit.value == 'Y':
                    return orig.replace(year=orig.year + value, day=day)
                if unit.value == 'E':
                    offset = orig - easter(year)
                    return easter(year+value) + offset
                raise Exception("Invalid DurationUnit %s" % unit)
            except ValueError:
                if day > 28:
                    day -= 1
                else:
                    raise

    def get_date_formatter(self):
        if self.value in 'YEM':
            return fds
        return day_and_month

class DurationUnits(dd.ChoiceList):
    verbose_name = _("Duration Unit")
    item_class = DurationUnit


add = DurationUnits.add_item
add('s', _('seconds'), 'seconds')
add('m', _('minutes'), 'minutes')
add('h', _('hours'), 'hours')
add('D', _('days'), 'days')
add('W', _('weeks'), 'weeks')
add('M', _('months'), 'months')
add('Y', _('years'), 'years')


class Recurrencies(dd.ChoiceList):
    verbose_name = _("Recurrency")
    item_class = DurationUnit

add = Recurrencies.add_item
add('O', _('once'), 'once')
add('D', _('daily'), 'daily')
add('W', _('weekly'), 'weekly')
add('M', _('monthly'), 'monthly')
add('Y', _('yearly'), 'yearly')
add('P', _('per weekday'), 'per_weekday')  # deprecated
add('E', _('Relative to Easter'), 'easter')


def amonthago():
    return DurationUnits.months.add_duration(dd.today(), -1)


class AccessClasses(dd.ChoiceList):
    verbose_name = _("Access Class")
add = AccessClasses.add_item
add('10', _('Private'), 'private')
add('20', _('Show busy'), 'show_busy')
add('30', _('Public'), 'public')


class PlannerColumns(dd.ChoiceList):
    verbose_name = _("Planner column")
add = PlannerColumns.add_item
add('10', _('External'), 'external')
add('20', _('Internal'), 'internal')



class TaskStates(dd.Workflow):
    """Possible values for the state of a :class:`Task`. The list of
    choices for the :attr:`Task.state` field. By default it contains
    the following values (which can be redefined in
    :attr:`workflows_module <lino.core.site.Site.workflows_module>`):

    """
    verbose_name_plural = _("Task states")
    required_roles = dd.login_required(dd.SiteStaff)
    app_label = 'cal'


add = TaskStates.add_item

add('10', _("To do"), 'todo')
add('15', _("Important"), 'important')
add('20', pgettext(u"cal", u"Started"), 'started')
add('30', _("Done"), 'done')
# add('40', _("Sleeping"),'sleeping')
add('50', _("Cancelled"), 'cancelled')


if not settings.SITE.use_silk_icons:
    TaskStates.todo.button_text = "☐"  # BALLOT BOX \u2610
    TaskStates.started.button_text = "☉"  # SUN (U+2609)	
    TaskStates.done.button_text = "☑"  # BALLOT BOX WITH CHECK \u2611
    TaskStates.cancelled.button_text = "☒"  # BALLOT BOX WITH X (U+2612)
    TaskStates.important.button_text = "⚠"  # U+26A0

class EntryState(dd.State):
    fixed = False
    edit_guests = False
    transparent = False
    noauto = False


class EntryStates(dd.Workflow):
    """The possible states of a calendar entry.

    Stored in the :attr:`state
    <lino_xl.lib.cal.models.Event.state>` field.

    """
    verbose_name_plural = _("Event states")
    required_roles = dd.login_required(dd.SiteStaff)
    app_label = 'cal'
    item_class = EntryState
    edit_guests = models.BooleanField(_("Edit participants"), default=False)
    fixed = models.BooleanField(_("Stable"), default=False)
    transparent = models.BooleanField(_("Transparent"), default=False)
    noauto = models.BooleanField(_("No auto"), default=False)
    # editable_states = set()
    # column_names = "value name text edit_guests"

    # @dd.virtualfield(models.BooleanField("edit_guests"))
    # def edit_guests(cls,obj,ar):
        # return obj.edit_guests

    @classmethod
    def get_column_names(self, ar):
        return 'value name text button_text edit_guests fixed transparent noauto'

add = EntryStates.add_item
add('10', _("Suggested"), 'suggested',
    edit_guests=True,
    button_text="?")
add('20', _("Draft"), 'draft', edit_guests=True,
    button_text="☐")  # BALLOT BOX (2610)
if False:
    add('40', _("Published"), 'published')
    # add('30', _("Notified"),'notified')
    add('30', _("Visit"), 'visit')
    add('60', _("Rescheduled"), 'rescheduled', fixed=True)
add('50', _("Took place"), 'took_place',
    fixed=True, edit_guests=True,
    button_text="☑")  # BALLOT BOX WITH CHECK (2611)

# lino_tera add a state "Missed"
# add('60', _("Missed"), 'missed', transparent=True,
#     help_text=_("Guest missed the appointment."),
#     button_text="☉", noauto=True)  # \u2609 SUN

add('70', _("Cancelled"), 'cancelled', fixed=True, transparent=True,
    help_text=_("Cancelled with valid reason."),
    button_text="☒", noauto=True)

if False:
    add('75', _("Omitted"), 'omitted', fixed=True, transparent=True,
        button_text="☒")  # BALLOT BOX WITH X (\u2612)
        # button_text="☹")  # 2639


class GuestState(dd.State):
    afterwards = False


class GuestStates(dd.Workflow):
    """
    Possible values for the state of a participation. The list of
    choices for the :attr:`Guest.state` field.

    The actual content can be redefined by other apps,
    e.g. :mod:`lino_xl.lib.reception`.
    """
    verbose_name_plural = _("Guest states")
    required_roles = dd.login_required(dd.SiteStaff)
    app_label = 'cal'
    item_class = GuestState
    afterwards = models.BooleanField(_("Afterwards"), default=False)

    @classmethod
    def get_column_names(self, ar):
        return 'value name afterwards text button_text'


add = GuestStates.add_item
add('10', _("Invited"), 'invited')

# GuestStates will be reset by importing either feedback or
# voga. But the calendar module itself requires a state named
# `invited`

