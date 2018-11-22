# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from django.db.models import Count

from lino.api import dd, rt, _

from lino.modlib.system.choicelists import ObservedEvent
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


class KnownContactType(dd.Choice):
    show_values = True
    _instance = None
    
    def create_object(self, **kwargs):
        kwargs.update(dd.str2kw('name', self.text))
        kwargs.update(known_contact_type=self)
        return rt.models.clients.ClientContactType(**kwargs)
    
    def get_object(self):
        if self._instance is None:
            M = rt.models.clients.ClientContactType
            try:
                self._instance = M.objects.get(known_contact_type=self)
            except M.DoesNotExist:
                return None
        return self._instance

    def get_contact(self, client):
        cct = self.get_object()
        if cct is None:
            return
        qs = rt.models.clients.ClientContact.objects.filter(
            client=client, type=cct)
        return qs.first()


class KnownContactTypes(dd.ChoiceList):
    verbose_name = _("Known contact type")
    verbose_name_plural = _("Known contact types")
    item_class = KnownContactType
    column_names = 'value name text db_object'
    required_roles = dd.login_required(ContactsStaff)

    @dd.virtualfield(dd.ForeignKey('clients.ClientContactType'))
    def db_object(cls, choice, ar):
        return choice.get_object()


add = KnownContactTypes.add_item

add('10', _("Coach"), 'coach')
add('20', _("Other"), 'other')
