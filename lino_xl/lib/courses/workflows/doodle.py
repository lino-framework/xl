# -*- coding: UTF-8 -*-
# Copyright 2013-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Defines the calendar workflows for a doodle-like system.

The responsible user of 

This is a :attr:`workflows_module
<lino.core.site.Site.workflows_module>`

"""

from lino.api import dd, _
from lino_xl.lib.cal.workflows import *
# from django.utils.translation import gettext_lazy as _
# from django.utils.translation import pgettext_lazy as pgettext

from lino_xl.lib.cal.choicelists import GuestStates, EntryStates
from lino_xl.lib.cal.actions import RefuseGuestStates


class MarkEventTookPlace(RefuseGuestStates):
    required_states = 'suggested draft cancelled'
    refuse_guest_states = 'invited'


class ResetEvent(dd.ChangeStateAction):
    """Reset this calendar entry to 'suggested' state."""
    button_text = EntryStates.suggested.button_text
    label = _("Reset")
    # show_in_workflow = True
    # show_in_bbar = False
    # required_states = 'draft took_place cancelled'
    required_states = 'suggested took_place cancelled'
    # readonly = False

    def get_action_permission(self, ar, obj, state):
        if obj.auto_type is None:
            return False
        return super(ResetEvent,
                     self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]

        def ok(ar):
            obj.state = EntryStates.suggested
            obj.save()
            ar.set_response(refresh=True)

        ar.confirm(ok,
                   _("Any manual changes to your event "
                     "will get lost upon next update "),
                   _("Are you sure?"))


GuestStates.clear()
add = GuestStates.add_item
# add('10', _("Invited"), 'invited', button_text="☐")
add('10', _("Invited"), 'invited', button_text="?")
add('40', _("Present"), 'present', afterwards=True, button_text="☑")
add('50', _("Missing"), 'missing', afterwards=True, button_text="☉")
add('60', _("Excused"), 'excused', button_text="⚕")
# add('10', "☐", 'invited')
# add('40', "☑", 'present', afterwards=True)
# add('50', "☉", 'missing', afterwards=True)
# add('60', "⚕", 'excused')


# @dd.receiver(dd.pre_analyze)
# def my_event_workflows(sender=None, **kw):

GuestStates.present.add_transition(
    # "\u2611",  # BALLOT BOX WITH CHECK
    required_states='invited')
    # help_text=_("Participant was present."))

GuestStates.missing.add_transition(
    # "☉",  # 2609 SUN
    required_states='invited')
    # help_text=_("Participant was absent."))

GuestStates.excused.add_transition(
    # "⚕",  # 2695
    required_states='invited')
    # help_text=_("Participant was excused."))

GuestStates.invited.add_transition(
    # "☐",  # BALLOT BOX \u2610
    required_states='missing present excused')
    # help_text=_("Reset state to invited."))

# sender.modules.cal.Event.find_next_date = FindNextDate()

"""

The transitions from a "final" state to another final state
(e.g. "took place" to "cancelled") exist just in case the user clicked
the wrong button.  Theoretically it is irritating to have this
possibility given because it suggests that some state change is still
expected.  They can go away for applications where the state field is
editable and where the users know how to use it. But for example in
:ref:`avanti` it isn't easily accessible.

"""

# EntryStates.suggested.add_transition(
# # "?",
# # _("Reset"),
# required_states='draft took_place cancelled')
# # help_text=_("Set to suggested state."))

EntryStates.suggested.add_transition(
    ResetEvent, name='reset_event')
    # "\u2610",  # BALLOT BOX
    # required_states='suggested took_place cancelled')
    # help_text=_("Set to draft state."))

EntryStates.draft.add_transition(
    required_states='suggested cancelled took_place')

EntryStates.took_place.add_transition(MarkEventTookPlace)
EntryStates.cancelled.add_transition(
    # "\u2609",  # SUN
    # pgettext("calendar event action", "Cancel"),
    #~ owner=True,
    # help_text=_("Event was cancelled."),
    required_states='suggested draft took_place')
    # icon_name='cross')
