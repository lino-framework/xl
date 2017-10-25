# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from django.db.models import Count

from lino.modlib.system.choicelists import ObservedEvent
from lino.api import dd, _

from lino_xl.lib.contacts.roles import ContactsStaff


class ClientEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
    max_length = 50


class ClientCreated(ObservedEvent):
    text = _("Created")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(created__gte=pv.start_date)
        if pv.end_date:
            qs = qs.filter(created__lte=pv.end_date)
        return qs

ClientEvents.add_item_instance(ClientCreated("created"))


class ClientModified(ObservedEvent):
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


class ClientStates(dd.Workflow):
    required_roles = dd.login_required(ContactsStaff)
    verbose_name_plural = _("Client states")
    default_value = 'newcomer'
    

add = ClientStates.add_item
add('10', _("Newcomer"), 'newcomer')  # "first contact" in Avanti
add('20', _("Refused"), 'refused')
add('30', _("Coached"), 'coached')
add('50', _("Former"), 'former')
