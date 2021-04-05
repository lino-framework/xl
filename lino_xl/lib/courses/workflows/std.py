# -*- coding: UTF-8 -*-
# Copyright 2012-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Importing this module will install default workflows for
`lino_xl.lib.courses`.

"""


from django.utils.translation import gettext_lazy as _
from lino_xl.lib.courses.choicelists import EnrolmentStates, CourseStates
from lino.api import dd, rt


class PrintAndChangeStateAction(dd.ChangeStateAction):

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]

        def ok(ar2):
            obj.do_print.run_from_ui(ar2, **kw)
            super(PrintAndChangeStateAction, self).run_from_ui(ar2)
            ar2.set_response(refresh_all=True)

        msg = self.get_confirmation_message(obj, ar)
        ar.confirm(ok, msg, _("Are you sure?"))

#~ class ConfirmEnrolment(PrintAndChangeStateAction):
    #~ required = dd.login_required(states='requested')
    #~ label = _("Confirm")
    #~
    #~ def get_confirmation_message(self,obj,ar):
        #~ return _("Confirm enrolment of <b>%(pupil)s</b> to <b>%(course)s</b>.") % dict(
            #~ pupil=obj.pupil,course=obj.course)


class CertifyEnrolment(PrintAndChangeStateAction):
    required_states = 'confirmed'
    label = _("Certify")
    #~ label = _("Award")
    #~ label = school.EnrolmentStates.award.text

    def get_confirmation_message(self, obj, ar):
        return _("Print certificate for <b>%(pupil)s</b>.") % dict(
            pupil=obj.pupil, course=obj.course)


class ConfirmEnrolment(dd.ChangeStateAction):
    """Confirm this enrolment.

    Sets the :attr:`state` to `confirmed` after Check for possible
    problems by calling :meth:`get_confirm_veto
    <lino_xl.lib.courses.models.Enrolment.get_confirm_veto>` to verify
    whether it is valid (e.g. whether there are enough free places).

    """
    label = _("Confirm")
    #~ icon_name = 'cancel'
    #~ required = dict(states='assigned',owner=True)
    # ~ required = dict(states='published rescheduled took_place')#,owner=True)
    required_states = 'requested'  # ,owner=True)

    def run_from_ui(self, ar, **kw):
        #~ problems = []
        for obj in ar.selected_rows:
            msg = obj.get_confirm_veto(ar)
            if msg is None:
                obj.state = EnrolmentStates.confirmed
                obj.save()
                ar.set_response(refresh_all=True)
            else:
                msg = _("Cannot confirm %(pupil)s : %(message)s") % dict(
                    pupil=obj.pupil, message=msg)
                ar.set_response(message=msg, alert=True)
                break


@dd.receiver(dd.pre_analyze)
def my_enrolment_workflows(sender=None, **kw):

    EnrolmentStates.confirmed.add_transition(ConfirmEnrolment)
    # EnrolmentStates.certified.add_transition(CertifyEnrolment)
    EnrolmentStates.cancelled.add_transition(
        required_states="confirmed requested")
    EnrolmentStates.requested.add_transition(
        required_states="trying confirmed cancelled")
    EnrolmentStates.trying.add_transition(
        required_states="requested confirmed cancelled")

    CourseStates.active.add_transition(
        required_states="draft inactive")
    CourseStates.draft.add_transition(
        required_states="active inactive closed")
    CourseStates.inactive.add_transition(
        required_states="draft active")
    CourseStates.closed.add_transition(
        required_states="draft active inactive")
