# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


import datetime
from dateutil.easter import easter
from dateutil.rrule import DAILY, WEEKLY, MONTHLY, YEARLY

from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd, _
from lino.utils.format_date import fds
# from lino.core.choicelists import ChoiceList


from .utils import day_and_month

class DisplayColors(dd.ChoiceList):
    verbose_name = _("Display color")
    verbose_name_plural = _("Display colors")
    required_roles = dd.login_required(dd.SiteStaff)
add = DisplayColors.add_item
cssColos = 'White Silver Gray Black Red Maroon Yellow Olive Lime Green Aqua Teal Blue Navy Fuchsia Purple'
for color in cssColos.split():
    add(color, _(color),color)

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

class YearMonths(dd.ChoiceList):
    verbose_name = _("YearMonths")
add = YearMonths.add_item
add('1', _('January'), 'january')
add('2', _('February'), 'february')
add('3', _('March'), 'march')
add('4', _('April'), 'april')
add('5', _('May'), 'may')
add('6', _('June'), 'june')
add('7', _('July'), 'july')
add('8', _('August'), 'august')
add('9', _('September'), 'september')
add('10', _('October'), 'october')
add('11', _('November'), 'november')
add('12', _('December'), 'december')


class DurationUnit(dd.Choice):

    du_freq = None  #dateutils frequency

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
    preferred_foreignkey_width = 12

add = Recurrencies.add_item
add('O', _('once'), 'once')
add('D', _('daily'), 'daily', du_freq=DAILY)
add('W', _('weekly'), 'weekly', du_freq=WEEKLY)
add('M', _('monthly'), 'monthly', du_freq=MONTHLY)
add('Y', _('yearly'), 'yearly', du_freq=YEARLY)
add('P', _('per weekday'), 'per_weekday')  # deprecated
add('E', _('Relative to Easter'), 'easter')


def amonthago():
    return DurationUnits.months.add_duration(dd.today(), -1)


class AccessClasses(dd.ChoiceList):
    verbose_name = _("Access class")
    verbose_name_plural = _("Access classes")
    required_roles = dd.login_required(dd.SiteStaff)
add = AccessClasses.add_item
add('10', _('Private'), 'private')
add('20', _('Show busy'), 'show_busy')
add('30', _('Public'), 'public')


class PlannerColumns(dd.ChoiceList):
    verbose_name = _("Planner column")
    verbose_name_plural = _("Planner columns")
    required_roles = dd.login_required(dd.SiteStaff)
add = PlannerColumns.add_item
add('10', _('External'), 'external')
add('20', _('Internal'), 'internal')



class TaskStates(dd.Workflow):
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

class GuestState(dd.State):
    afterwards = False


class GuestStates(dd.Workflow):
    verbose_name_plural = _("Presence states")
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



class EntryState(dd.State):
    fixed = False
    fill_guests = False
    transparent = False
    noauto = False
    guest_state = None

class EventEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = EventEvents.add_item
add('10', _("Stable"), 'stable')
add('20', _("Unstable"), 'pending')

class EntryStates(dd.Workflow):
    verbose_name_plural = _("Entry states")
    required_roles = dd.login_required(dd.SiteStaff)
    app_label = 'cal'
    item_class = EntryState
    fill_guests = models.BooleanField(_("Fill guests"), default=False)
    fixed = models.BooleanField(_("Stable"), default=False)
    transparent = models.BooleanField(_("Transparent"), default=False)
    noauto = models.BooleanField(_("No auto"), default=False)
    guest_state = GuestStates.field(_("Guest state"), blank=True)
    # editable_states = set()
    # column_names = "value name text fill_guests"

    # @dd.virtualfield(models.BooleanField("fill_guests"))
    # def fill_guests(cls,obj,ar):
        # return obj.fill_guests

    @classmethod
    def get_column_names(self, ar):
        return 'value name text button_text fill_guests fixed transparent noauto'

add = EntryStates.add_item
add('10', _("Suggested"), 'suggested',
    fill_guests=True,
    button_text="?")
add('20', _("Draft"), 'draft', fill_guests=True,
    button_text="☐")  # BALLOT BOX (2610)
if False:
    add('40', _("Published"), 'published')
    # add('30', _("Notified"),'notified')
    add('30', _("Visit"), 'visit')
    add('60', _("Rescheduled"), 'rescheduled', fixed=True)
add('50', _("Took place"), 'took_place',
    fixed=True, fill_guests=False,
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
