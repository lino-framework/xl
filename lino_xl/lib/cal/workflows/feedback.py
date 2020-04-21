# -*- coding: UTF-8 -*-
# Copyright 2013-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Adds feedback-based workflow to :mod:`lino_xl.lib.cal`.

Used e.g. by :ref:`welfare`.

"""

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.conf import settings

from lino.modlib.notify.actions import NotifyingAction
from lino.api import dd

from lino_xl.lib.cal.choicelists import EntryStates, GuestStates

add = EntryStates.add_item
# add('40', _("Notified"), 'published', fill_guests=True,
add('40', _("Published"), 'published', fill_guests=True,
    fixed=True, button_text="☼")   # WHITE SUN WITH RAYS (U+263C)

# EntryStates.new.button_text ="⛶"  # SQUARE FOUR CORNERS (U+26F6)
# EntryStates.talk.button_text ="⚔"  # CROSSED SWORDS (U+2694)
# EntryStates.opened.button_text = "☉"  # SUN (U+2609)
# # EntryStates.started.button_text="☭"  # HAMMER AND SICKLE (U+262D)
# EntryStates.started.button_text = "⚒"  # HAMMER AND PICK (U+2692
# EntryStates.sticky.button_text="♥"  # BLACK HEART SUIT (U+2665)
# EntryStates.sleeping.button_text = "☾"  # LAST QUARTER MOON (U+263E)
# EntryStates.ready.button_text = "☐"  # BALLOT BOX \u2610
# EntryStates.closed.button_text = "☑"  # BALLOT BOX WITH CHECK \u2611
# EntryStates.cancelled.button_text="☒"  # BALLOT BOX WITH X (U+2612)


GuestStates.clear()
add = GuestStates.add_item
add('10', _("Invited"), 'invited')
add('20', _("Accepted"), 'accepted')
add('30', _("Rejected"), 'rejected')
add('40', _("Present"), 'present', afterwards=True)
add('50', _("Absent"), 'missing', afterwards=True)
add('60', _("Excused"), 'excused', afterwards=True)

GuestStates.present_states = set([GuestStates.present])

class InvitationFeedback(dd.ChangeStateAction, NotifyingAction):
    """Base class for actions that give feedback to an invitation.

    """
    def get_notify_owner(self, ar, obj):
        return obj.event

    def get_notify_recipients(self, ar, obj):
        yield (obj.user, obj.user.mail_mode)

    def get_action_permission(self, ar, obj, state):
        if obj.partner_id is None:
            return False
        if obj.event.state != EntryStates.published:
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
        return obj.event_id and (obj.event.state == EntryStates.took_place)


class MarkAbsent(dd.ChangeStateAction):
    """Mark this participant as absent (without explanation).

    """
    label = _("Absent")

class MarkExcused(dd.ChangeStateAction):
    """Mark this participant as absent (with acceptable explanation).

    """
    label = _("Excused")

class ResetEvent(dd.ChangeStateAction):
    label = _("Reset")
    if settings.SITE.use_silk_icons:
        icon_name = 'cancel'
    required_states = 'published took_place'

class CancelEvent(dd.ChangeStateAction):
    label = pgettext("calendar event action", "Cancel")
    required_states = 'suggested published draft'
    if settings.SITE.use_silk_icons:
        icon_name = 'cross'


class PublishEvent(dd.ChangeStateAction):
    """Mark this event as published.  All participants have been informed.

    (Disabled rule: You cannot publish a meeting which lies in the past.)

    """
    label = _("Publish")
    required_states = 'suggested draft'
    if settings.SITE.use_silk_icons:
        icon_name = 'accept'

    def unused_get_action_permission(self, ar, obj, state):
        d = obj.end_date or obj.start_date
        if d < dd.today():
            return False
        return super(PublishEvent,
                     self).get_action_permission(ar, obj, state)


class CloseMeeting(dd.ChangeStateAction):
    """The meeting is over and the guests go home.

    You cannot close a meeting that lies in the future.

    """
    label = _("Close meeting")
    # help_text = _("The event took place.")
    if settings.SITE.use_silk_icons:
        icon_name = 'emoticon_smile'
    required_states = 'suggested published draft'

    def get_action_permission(self, ar, obj, state):
        d = obj.end_date or obj.start_date
        if d > dd.today():
            return False
        return super(CloseMeeting,
                     self).get_action_permission(ar, obj, state)

GuestStates.accepted.add_transition(AcceptInvitation)
GuestStates.rejected.add_transition(RejectInvitation)
GuestStates.present.add_transition(MarkPresent)
GuestStates.missing.add_transition(MarkAbsent)
GuestStates.excused.add_transition(MarkExcused)


EntryStates.published.add_transition(PublishEvent)
# EntryStates.published.add_transition(  # _("Confirm"),
#     required_states='suggested draft',
#     icon_name='accept',
#     help_text=_("Mark this as published. "
#                 "All participants have been informed."))
EntryStates.took_place.add_transition(CloseMeeting, name='close_meeting')
EntryStates.cancelled.add_transition(CancelEvent)
# EntryStates.omitted.add_transition(required_states="suggested draft published")
EntryStates.draft.add_transition(ResetEvent)
