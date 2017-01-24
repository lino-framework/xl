# -*- coding: UTF-8 -*-
# Copyright 2008-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""Choicelists for this plugin.

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.db.models import Count

from lino.modlib.system.choicelists import ObservedEvent
from lino.api import dd, _

from .utils import only_coached_on
from .roles import CoachingsStaff


class ClientEvents(dd.ChoiceList):
    """A choicelist of observable client events.

    """
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
    max_length = 50


# class ClientIsActive(ObservedEvent):
#     text = _("Active")

#     def add_filter(self, qs, pv):
#         period = (pv.start_date, pv.end_date)
#         qs = only_coached_on(qs, period)
#         return qs

# ClientEvents.add_item_instance(ClientIsActive("active"))


class ClientHasCoaching(ObservedEvent):
    text = _("Coaching")

    def add_filter(self, qs, pv):
        period = (pv.start_date, pv.end_date)
        qs = only_coached_on(qs, period)
        return qs

ClientEvents.add_item_instance(ClientHasCoaching("active"))


class ClientCreated(ObservedEvent):
    """The choice for :class:`ClientEvents` which
    selects clients whose record has been *created* during the observed
    period.
    """
    text = _("Created")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(created__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(created__lte=pv.end_date)
        return qs

ClientEvents.add_item_instance(ClientCreated("created"))


class ClientModified(ObservedEvent):
    """The choice for :class:`ClientEvents` which selects clients whose
    main record has been *modified* during the observed period.

    """
    text = _("Modified")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(modified__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(modified__lte=pv.end_date)
        return qs

ClientEvents.add_item_instance(ClientModified("modified"))


class ClientHasNote(ObservedEvent):
    text = _("Note")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(
                notes_note_set_by_project__date__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(
                notes_note_set_by_project__date__lte=pv.end_date)
        qs = qs.annotate(num_notes=Count('notes_note_set_by_project'))
        qs = qs.filter(num_notes__gt=0)
        # print(20150519, qs.query)
        return qs

ClientEvents.add_item_instance(ClientHasNote("note"))


# elif ce == ClientEvents.dispense:
#     qs = qs.filter(
#         dispense__end_date__gte=period[0],
#         dispense__start_date__lte=period[1]).distinct()
# elif ce == ClientEvents.created:
#     qs = qs.filter(
#         created__gte=datetime.datetime.combine(
#             period[0], datetime.time()),
#         created__lte=datetime.datetime.combine(
#             period[1], datetime.time()))
#     #~ print 20130527, qs.query
# elif ce == ClientEvents.modified:
#     qs = qs.filter(
#         modified__gte=datetime.datetime.combine(
#             period[0], datetime.time()),
#         modified__lte=datetime.datetime.combine(
#             period[1], datetime.time()))
# elif ce == ClientEvents.penalty:
#     qs = qs.filter(
#         exclusion__excluded_until__gte=period[0],
#         exclusion__excluded_from__lte=period[1]).distinct()
# elif ce == ClientEvents.note:
#     qs = qs.filter(
#         notes_note_set_by_project__date__gte=period[0],
#         notes_note_set_by_project__date__lte=period[1]).distinct()


# add = ClientEvents.add_item
# add('10', _("Active"), 'active')
# add('20', _("ISIP"), 'isip')
# add('21', _("Art60§7 job supplyment"), 'jobs')
# add('22', _("Dispense"), 'dispense')
# if dd.is_installed('immersion'):
#     add('23', _("Immersion training"), 'immersion')
# if dd.is_installed('art61'):
#     add('24', _("Art61 job supplyment"), 'art61')
# add('30', _("Penalty"), 'penalty')
# add('31', _("Exclusion"), 'exclusion')
# add('40', _("Note"), 'note')
# add('50', _("Created"), 'created')
# add('60', _("Modified"), 'modified')
# add('70', _("Available"), 'available')


class ClientStates(dd.Workflow):
    required_roles = dd.required(CoachingsStaff)
    verbose_name_plural = _("Client states")

add = ClientStates.add_item
add('10', _("Newcomer"), 'newcomer')  # "first contact" in Avanti
add('20', _("Refused"), 'refused')
add('30', _("Coached"), 'coached')
add('50', _("Former"), 'former')
