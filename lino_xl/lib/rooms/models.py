# -*- coding: UTF-8 -*-
# Copyright 2013-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from django.db import models
from django.conf import settings

from lino.api import dd, _
from lino import mixins
from lino.mixins.registrable import RegistrableState
from lino_xl.lib.cal.choicelists import Recurrencies
from lino_xl.lib.cal.mixins import Reservation, ReservationStates
from lino_xl.lib.contacts.mixins import ContactRelated
from lino.modlib.office.roles import OfficeStaff

class BookingStates(ReservationStates):
    item_class = RegistrableState
    required_roles = dd.login_required(OfficeStaff)
    auto_update_calendar = models.BooleanField(_("Update calendar"), default=True)

add = BookingStates.add_item
add('10', _("Draft"), 'draft', is_editable=True)
add('20', _("Option"), 'option', is_editable=False)
add('30', _("Registered"), 'registered', is_editable=False)
add('40', _("Cancelled"), 'cancelled', is_editable=False)


@dd.receiver(dd.pre_analyze)
def setup_rooms_workflow(sender=None, **kw):

    #~ BookingStates.draft.add_transition(
        #~ states='option registered cancelled',
        #~ icon_name="pencil")
    #~ BookingStates.registered.add_transition(_("Register"),
        #~ states='draft option',
        #~ icon_name="accept")

    #~ Bookings.deregister_action.add_requirements(states='option registered cancelled')
    #~ Bookings.register_action.add_requirements(states='option draft cancelled')
    BookingStates.draft.add_transition(
        required_states='registered option cancelled',
        icon_name="pencil")
    BookingStates.option.add_transition(
        required_states='draft registered',
        icon_name="eye",
        help_text=_("Optionally booked. Ask customer before any decision."))
    BookingStates.registered.add_transition(
        required_states='draft option cancelled',
        icon_name="accept")
    BookingStates.cancelled.add_transition(
        required_states='draft option registered',
        icon_name='cross')



class Booking(ContactRelated, Reservation):

    class Meta:
        abstract = dd.is_abstract_model(__name__, 'Booking')
        verbose_name = _("Booking")
        verbose_name_plural = _('Bookings')

    #~ workflow_state_field = 'state'

    state = BookingStates.field(default=BookingStates.as_callable('draft'))
    event_type = dd.ForeignKey('cal.EventType', null=True, blank=True,
        help_text=_("""The calendar entry type of the calendar entries to generate."""))

    def __str__(self):
        return u"%s #%s (%s)" % (self._meta.verbose_name, self.pk, self.room)

    # def update_cal_from(self, ar):
    #     return self.start_date

    # def update_cal_until(self):
    #     return self.end_date

    def update_cal_event_type(self):
        return self.event_type

    def update_cal_summary(self, et, i):
        if self.every_unit == Recurrencies.once:
            return dd.babelattr(et, 'event_label')
        return "%s %s" % (dd.babelattr(et, 'event_label'), i)

    def before_auto_event_save(self, event):
        """Sets room for automatic events.

        """
        assert not settings.SITE.loading_from_dump
        assert event.owner == self
        super(Booking, self).before_auto_event_save(event)
        if event.is_user_modified():
            return
        event.room = self.room

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(Booking, cls).get_registrable_fields(site):
            yield f
        yield 'company'
        yield 'contact_person'
        yield 'event_type'

    # don't inherit default actions:
    #~ register_action = None
    #~ deregister_action = None

    def before_state_change(self, ar, old, new):
        if new.name == 'registered':
            if self.get_existing_auto_events().count() == 0:
                #~ ar.confirm("Booking has no events! Are you sure?")
                raise Warning("Booking has no events!")

    def after_ui_save(self, ar, cw):
        super(Booking, self).after_ui_save(ar, cw)
        if self.state.is_editable:
            self.update_reminders(ar)


dd.update_field(Booking, 'contact_person', verbose_name=_("Contact person"))
dd.update_field(Booking, 'company', verbose_name=_("Organizer"))
dd.update_field(Booking, 'every_unit',
                default=Recurrencies.as_callable('once'))
dd.update_field(Booking, 'every', default=1)


class BookingDetail(dd.DetailLayout):
    #~ start = "start_date start_time"
    #~ end = "end_date end_time"
    #~ freq = "every every_unit"
    #~ start end freq
    main = "general invoicing.InvoicingsByGenerator"
    general = dd.Panel("""
    start_date start_time end_date end_time
    room event_type workflow_buttons
    max_events max_date every_unit every
    monday tuesday wednesday thursday friday saturday sunday
    company contact_person user id:8
    cal.EntriesByController
    """, label=_("General"))

    #~ def setup_handle(self,dh):
        #~ dh.start.label = _("Start")
        #~ dh.end.label = _("End")
        #~ dh.freq.label = _("Frequency")


class Bookings(dd.Table):
    required_roles = dd.login_required(OfficeStaff)
    model = 'rooms.Booking'
    #~ order_by = ['date','start_time']
    detail_layout = BookingDetail()
    insert_layout = """
    start_date start_time end_time
    room event_type
    company contact_person
    """
    column_names = "start_date company room  *"
    order_by = ['start_date']

    parameters = mixins.ObservedDateRange(
        company=dd.ForeignKey('contacts.Company', blank=True, null=True),
        state=BookingStates.field(blank=True),
    )
    params_layout = """company state"""

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(Bookings, cls).get_simple_parameters())
        s.append('company')
        return s

    # simple_parameters = 'company state'.split()

    @classmethod
    def get_request_queryset(self, ar, **filter):
        qs = super(Bookings, self).get_request_queryset(ar, **filter)
        if isinstance(qs, list):
            return qs
        # for n in self.simple_param_fields:
        #     v = ar.param_values.get(n)
        #     if v:
        #         qs = qs.filter(**{n: v})
        #         #~ print 20130530, qs.query

        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Bookings, self).get_title_tags(ar):
            yield t

        # for n in self.simple_param_fields:
        #     v = ar.param_values.get(n)
        #     if v:
        #         yield unicode(v)


class BookingsByCompany(Bookings):
    master_key = "company"
