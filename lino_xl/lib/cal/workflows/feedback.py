# -*- coding: UTF-8 -*-
# Copyright 2013-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Adds feedback-based workflow to :mod:`lino_xl.lib.cal`. You
"activate" this by simply importing it from within a
:xfile:`models.py` module used by your application.

Used e.g. by :ref:`welfare`.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from lino.modlib.notify.actions import NotifyingAction
from lino.api import dd

from ..workflows import EventStates, GuestStates

add = EventStates.add_item
add('40', _("Notified"), 'published', edit_guests=True)


GuestStates.clear()
add = GuestStates.add_item
add('10', _("Invited"), 'invited')
add('20', _("Accepted"), 'accepted')
add('30', _("Rejected"), 'rejected')
add('40', _("Present"), 'present', afterwards=True)
add('50', _("Absent"), 'absent', afterwards=True)
add('60', _("Excused"), 'excused', afterwards=True)

class InvitationFeedback(dd.ChangeStateAction, NotifyingAction):
    """Base class for actions that give feedback to an invitation.

    """
    def get_notify_owner(self, ar, obj):
        return obj.event

    def get_notify_recipients(self, ar, obj):
        yield obj.user

    def get_action_permission(self, ar, obj, state):
        if obj.partner_id is None:
            return False
        if obj.event.state != EventStates.published:
            return False
        return super(InvitationFeedback,
                     self).get_action_permission(ar, obj, state)

    def get_notify_subject(self, ar, obj):
        return self.notify_subject % dict(
            guest=obj.partner,
            event_type=obj.event.event_type,
            day=dd.fds(obj.event.start_date),
            time=str(obj.event.start_time))


class RejectInvitation(InvitationFeedback):
    label = _("Reject")
    help_text = _("Reject this invitation.")
    required_states = 'invited accepted'
    notify_subject = _(
        "%(guest)s cannot accept invitation "
        "to %(event_type)s on %(day)s at %(time)s")


class AcceptInvitation(InvitationFeedback):
    """Accept this invitation.
    """
    label = _("Accept")
    required_states = 'invited rejected'
    notify_subject = _("%(guest)s has accepted the invitation "
                       "to %(event_type)s on %(day)s at %(time)s")


class MarkPresent(dd.ChangeStateAction):
    """Mark this participant as present at the event.

    """
    
    label = _("Present")
    # required_states = 'invited accepted'

    def get_action_permission(self, ar, obj, state):
        if not super(MarkPresent, self).get_action_permission(ar, obj, state):
            return False
        return obj.event_id and (obj.event.state == EventStates.took_place)


class MarkAbsent(MarkPresent):
    """Mark this participant as absent at the event (without explanation).

    """    
    label = _("Absent")

class MarkExcused(MarkPresent):
    """Mark this participant as absent at the event (with acceptable
    explanation).

    """    
    label = _("Excused")




class ResetEvent(dd.ChangeStateAction):
    label = _("Reset")
    icon_name = 'cancel'
    required_states = 'published took_place'


class CloseMeeting(dd.ChangeStateAction):
    """To close a meeting means that the meeting is over and the guests go
    home.

    """
    label = _("Close meeting")
    help_text = _("The event took place.")
    icon_name = 'emoticon_smile'
    required_states = 'published draft'

    def get_action_permission(self, ar, obj, state):
        d = obj.end_date or obj.start_date
        if d > dd.today():
            return False
        return super(CloseMeeting,
                     self).get_action_permission(ar, obj, state)

GuestStates.accepted.add_transition(AcceptInvitation)
GuestStates.rejected.add_transition(RejectInvitation)
GuestStates.present.add_transition(MarkPresent)
GuestStates.absent.add_transition(MarkAbsent)
GuestStates.excused.add_transition(MarkExcused)


EventStates.published.add_transition(  # _("Confirm"),
    required_states='suggested draft',
    icon_name='accept',
    help_text=_("Mark this as published. "
                "All participants have been informed."))
EventStates.took_place.add_transition(CloseMeeting, name='close_meeting')
EventStates.cancelled.add_transition(
    pgettext("calendar event action", "Cancel"),
    required_states='published draft',
    icon_name='cross')
EventStates.draft.add_transition(ResetEvent)
