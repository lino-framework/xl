# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Some standard workflow definition modules for
:mod:`lino_xl.lib.cal`.

.. autosummary::
   :toctree:

    feedback

"""

from __future__ import unicode_literals


from django.db import models
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext


from lino.api import dd


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
add('20', pgettext(u"cal", u"Started"), 'started')
add('30', _("Done"), 'done')
# add('40', _("Sleeping"),'sleeping')
add('50', _("Cancelled"), 'cancelled')


if not settings.SITE.use_silk_icons:
    TaskStates.todo.button_text = "☐"  # BALLOT BOX \u2610
    TaskStates.started.button_text = "☉"  # SUN (U+2609)	
    TaskStates.done.button_text = "☑"  # BALLOT BOX WITH CHECK \u2611
    TaskStates.cancelled.button_text = "☒"  # BALLOT BOX WITH X (U+2612)

class EventState(dd.State):
    fixed = False
    edit_guests = False
    transparent = False
    noauto = False


class EventStates(dd.Workflow):
    """The list of choices for the :attr:`state
    <lino_xl.lib.cal.models.Event.state>` field of a calendar entry.

    """
    verbose_name_plural = _("Event states")
    required_roles = dd.login_required(dd.SiteStaff)
    help_text = _("""The possible states of a calendar event.""")
    app_label = 'cal'
    item_class = EventState
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

add = EventStates.add_item
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

add('70', _("Cancelled"), 'cancelled', fixed=True, transparent=True,
    # button_text="\u2609", noauto=True)  # SUN
    button_text="☒", noauto=True)  # BALLOT BOX WITH X (\u2612)

if False:
    add('75', _("Omitted"), 'omitted', fixed=True, transparent=True,
        button_text="☒")  # BALLOT BOX WITH X (\u2612)
        # button_text="☹")  # 2639
# add('80', _("Absent"), 'absent')


class GuestState(dd.State):
    afterwards = False


class GuestStates(dd.Workflow):
    """Possible values for the state of a Guest. The list of choices for
    the :attr:`Guest.state` field.

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


def f(name):
    if settings.SITE.use_silk_icons:
        return name

TaskStates.todo.add_transition(
    _("Reopen"), required_states='done cancelled')

TaskStates.done.add_transition(
    required_states='todo started', icon_name=f('accept'))
TaskStates.cancelled.add_transition(
    required_states='todo started', icon_name=f('cancel'))
