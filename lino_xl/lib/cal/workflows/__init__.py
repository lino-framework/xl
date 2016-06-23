# -*- coding: UTF-8 -*-
# Copyright 2011-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

"""Some standard workflow definition modules for
:mod:`lino_xl.lib.cal`.

.. autosummary::
   :toctree:

    feedback
    take
    voga

"""

from __future__ import unicode_literals


from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd


class TaskStates(dd.Workflow):
    """Possible values for the state of a :class:`Task`. The list of
    choices for the :attr:`Task.state` field. By default it contains
    the following values (which can be redefined in
    :meth:`lino.core.site.Site.setup_choicelists`):

    .. django2rst::

            rt.show(cal.TaskStates)

    """
    verbose_name_plural = _("Task states")
    required_roles = dd.required(dd.SiteStaff)
    app_label = 'cal'


add = TaskStates.add_item

add('10', _("To do"), 'todo')
add('20', pgettext(u"cal", u"Started"), 'started')
add('30', _("Done"), 'done')
# add('40', _("Sleeping"),'sleeping')
add('50', _("Cancelled"), 'cancelled')


class EventState(dd.State):
    fixed = False
    edit_guests = False
    transparent = False
    noauto = False


class EventStates(dd.Workflow):
    """Possible values for the state of a task. The list of choices for
    the :attr:`Event.state` field. By default it contains the
    following values (which can be redefined in
    :meth:`lino.core.site.Site.setup_choicelists`):

    .. django2rst::

            rt.show(cal.EventStates)

    """
    verbose_name_plural = _("Event states")
    required_roles = dd.required(dd.SiteStaff)
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
    button_text="?",
    # button_text="♍",  # Virgo
    help_text=_("Automatically suggested. "
                "Default state of an automatic event."))
add('20', _("Draft"), 'draft', edit_guests=True,
    button_text="\u2610")  # BALLOT BOX
if False:
    add('40', _("Published"), 'published')
    # add('30', _("Notified"),'notified')
    add('30', _("Visit"), 'visit')
    add('60', _("Rescheduled"), 'rescheduled', fixed=True)
add('50', _("Took place"), 'took_place',
    fixed=True, edit_guests=True,
    button_text="\u2611")  # BALLOT BOX WITH CHECK

add('70', _("Cancelled"), 'cancelled', fixed=True, transparent=True,
    button_text="\u2609", noauto=True)  # SUN
add('75', _("Omitted"), 'omitted', fixed=True, transparent=True,
    button_text="\u2612")  # BALLOT BOX WITH X
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
    required_roles = dd.required(dd.SiteStaff)
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


@dd.receiver(dd.pre_analyze)
def setup_task_workflows(sender=None, **kw):

    TaskStates.todo.add_transition(
        _("Reopen"), required_states='done cancelled')
    TaskStates.done.add_transition(
        required_states='todo started', icon_name='accept')
    TaskStates.cancelled.add_transition(
        required_states='todo started', icon_name='cancel')
