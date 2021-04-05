# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from __future__ import unicode_literals

"""Importing this module will install default workflows for
`lino_xl.lib.meetings`.

"""

from lino.api import dd, rt, _

from .choicelists import MeetingStates


class StartMeeting(dd.ChangeStateAction):
    required_states = 'draft inactive'
    help_text = _("Record Ticket States and start the meeting.")

    def run_from_ui(self, ar, **kw):
        #~ problems = []
        for obj in ar.selected_rows:
            qs = obj.wishes_by_milestone.select_related('ticket')
            for de in qs:
                de.old_ticket_state = de.ticket.state
                de.full_clean()
                de.save()
        obj.state = MeetingStates.active
        obj.save()
        ar.set_response(refresh_all=True)

class DraftMeeting(dd.ChangeStateAction):
    required_states = "active inactive closed"
    help_text = _("Record Ticket States and start the meeting.")

    def run_from_ui(self, ar, **kw):
        # ~ problems = []
        sl = ar.selected_rows
        def OK(ar):
            for obj in sl:
                obj.wishes_by_milestone.update(new_ticket_state=None,
                                               old_ticket_state=None)
                obj.state = MeetingStates.draft
                obj.save()
                ar.set_response(refresh_all=True)

        ar.confirm(OK, _("Remove wish's ticket States?"))

class FinishMeeting(dd.ChangeStateAction):
    required_states = 'draft active inactive'
    help_text = _("Record Ticket States and start the meeting.")

    def run_from_ui(self, ar, **kw):
        # ~ problems = []
        sl = ar.selected_rows

        must_update = []
        for obj in sl:
            qs = obj.wishes_by_milestone.exclude().select_related('ticket')
            for de in qs:
                if de.new_ticket_state is not None:
                    if de.ticket.state != de.new_ticket_state:
                        must_update.append((de.ticket, de.new_ticket_state))
        obj.state = MeetingStates.closed
        obj.save()
        ar.set_response(refresh_all=True)
            
        def ok(ar2):
            for (ticket, st) in must_update:
                ticket.state = de.new_ticket_state
                ticket.full_clean()
                ticket.save()

        if len(must_update) > 0:
            ar.confirm(ok, _("Finish meeting and set all tickets to their new state?"))
#
# @dd.receiver(dd.pre_analyze)
# def my_enrolment_workflows(sender=None, **kw):

MeetingStates.active.add_transition(StartMeeting)
MeetingStates.draft.add_transition(DraftMeeting)
MeetingStates.inactive.add_transition(
    required_states="draft active")
MeetingStates.closed.add_transition(FinishMeeting)
