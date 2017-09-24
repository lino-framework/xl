# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

import datetime
from dateutil.easter import easter

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


