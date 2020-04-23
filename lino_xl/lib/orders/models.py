# -*- coding: UTF-8 -*-
# Copyright 2019-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

# from decimal import Decimal
from lino_xl.lib.ledger.utils import ZERO, ONE

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils.text import format_lazy
from etgen.html import E, join_elems, tostring

from lino.api import dd, rt
from lino import mixins

from lino.mixins import ProjectRelated
from lino.mixins.human import parse_name
from lino.mixins.duplicable import Duplicable
from lino.mixins.periods import DateRange
# from lino.mixins.registrable import Registrable
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.excerpts.mixins import ExcerptTitle
from lino.modlib.users.mixins import UserAuthored
from lino.modlib.printing.mixins import Printable
# from lino.modlib.printing.utils import PrintableObject
# from lino_xl.lib.cal.mixins import Reservation
from lino_xl.lib.cal.choicelists import Recurrencies
from lino_xl.lib.cal.utils import day_and_month
from lino_xl.lib.cal.mixins import RecurrenceSet, EventGenerator
from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.ledger.models import RegistrableVoucher
from lino_xl.lib.ledger.mixins import SequencedVoucherItem
# from lino_xl.lib.sales.mixins import SalesDocument, ProductDocItem
from lino_xl.lib.excerpts.mixins import Certifiable

from lino.utils.dates import DateRangeValue

# from .actions import PrintPresenceSheet
from .choicelists import OrderStates

try:
    worker_model = dd.plugins.orders.worker_model
    worker_name_fields = dd.plugins.orders.worker_name_fields
except AttributeError:
    # Happens only when Sphinx autodoc imports it and this module is
    # not installed.
    worker_model = 'foo.Bar'
    worker_name_fields = 'foo bar'

from lino.modlib.uploads.mixins import UploadController

#
# class Order(SalesDocument, UserAuthored, UploadController, RecurrenceSet, EventGenerator, Duplicable):
# class Order(SalesDocument, Voucher, RecurrenceSet, EventGenerator, Duplicable):
# class Order(Registrable, Certifiable, Voucher, RecurrenceSet, EventGenerator, Duplicable, ProjectRelated):
class Order(Certifiable, RegistrableVoucher, RecurrenceSet, EventGenerator, Duplicable, ProjectRelated):

    class Meta:
        app_label = 'orders'
        abstract = dd.is_abstract_model(__name__, 'Order')
        verbose_name = _("Order")
        verbose_name_plural = _('Orders')

    hide_editable_number = False
    quick_search_fields = "subject project__name"

    state = OrderStates.field(default='draft')

    # order_area = OrderAreas.field(default='default')
    # client = dd.ForeignKey(
    #     "presto.Client",
    #     related_name="%(app_label)s_%(class)s_set_by_client",
    #     blank=True, null=True)
    #
    invoice_recipient = dd.ForeignKey(
        'contacts.Partner',
        verbose_name=_("Invoice recipient"),
        related_name='orders_by_recipient',
        blank=True, null=True)

    subject = models.CharField(_("Our reference"), max_length=200, blank=True)
    # site_field_name = 'room'

    # line = dd.ForeignKey('orders.Line')
    # event_type = dd.ForeignKey('cal.EventType', null=True, blank=True)
    # room = dd.ForeignKey('cal.Room', blank=True)
    description = dd.TextField(_("Description"), blank=True)
    remark = models.TextField(_("Remark"), blank=True)
    # entry_date = models.DateField(
    #     verbose_name=_("Entry date"))
    max_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Generate events until"))
    # order_state = OrderStates.field(default='draft')

    # quick_search_fields = 'name'

    # max_places = models.PositiveIntegerField(
    #     pgettext("in a order", "Available places"),
    #     help_text=("Maximum number of participants"),
    #     blank=True, null=True)
    #
    # name = models.CharField(_("Designation"), max_length=100, blank=True)
    # enrolments_until = models.DateField(
    #     _("Enrolments until"), blank=True, null=True)
    #
    # print_presence_sheet = PrintPresenceSheet(show_in_bbar=False)
    # print_presence_sheet_html = PrintPresenceSheet(
    #     show_in_bbar=False,
    #     build_method='weasy2html',
    #     label=format_lazy(u"{}{}",_("Presence sheet"), _(" (HTML)")))

    def get_worker_choices(self):
        worker = dd.resolve_model(worker_model)
        return worker.objects.all()

    def full_clean(self, *args, **kwargs):
        if self.entry_date is None:
            self.entry_date = dd.today()
        super(Order, self).full_clean(*args, **kwargs)

    # @dd.displayfield(_("Print"))
    # def print_actions(self, ar):
    #     if ar is None:
    #         return ''
    #     elems = []
    #     elems.append(ar.instance_action_button(
    #         self.print_presence_sheet))
    #     elems.append(ar.instance_action_button(
    #         self.print_presence_sheet_html))
    #     return E.p(*join_elems(elems, sep=", "))

    # def on_duplicate(self, ar, master):
    #     self.state = OrderStates.draft
    #     super(Order, self).on_duplicate(ar, master)
    #
    def update_cal_until(self):
        return self.max_date

    def get_partner(self):
        if self.invoice_recipient is not None:
            return self.invoice_recipient
        if self.project is not None:
            return self.project.get_partner()

    def get_wanted_movements(self):
        return []

    # @classmethod
    # def add_param_filter(
    #         cls, qs, lookup_prefix='', show_exposed=None, **kwargs):
    #     qs = super(Order, cls).add_param_filter(qs, **kwargs)
    #     exposed_states = OrderStates.filter(is_exposed=True)
    #     fkw = dict()
    #     fkw[lookup_prefix + 'state__in'] = exposed_states
    #     if show_exposed == dd.YesNo.no:
    #         qs = qs.exclude(**fkw)
    #     elif show_exposed == dd.YesNo.yes:
    #         qs = qs.filter(**fkw)
    #     return qs

    @classmethod
    def get_simple_parameters(cls):
        for f in super(Order, cls).get_simple_parameters():
            yield f
        yield 'journal__room'

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(Order, cls).get_registrable_fields(site):
            yield f
        yield 'name'

    def update_cal_rset(self):
        return self

    def update_cal_from(self, ar):
        """Note: if recurrency is weekly or per_weekday, actual start may be
        later than self.start_date

        """
        # if self.state in (OrderStates.draft, OrderStates.cancelled):
        # if self.state == OrderStates.cancelled:
        #     ar.info("No start date because state is %s", self.state)
        #     return None
        return self.start_date

    def update_cal_event_type(self):
        if self.journal.room_id:
            return self.journal.room.event_type

    def update_cal_summary(self, et, i):
        if self.every_unit == Recurrencies.once:
            return str(self)
        return "%s %s" % (dd.babelattr(et, 'event_label'), i)

    # def get_events_user(self):
    #     """The user of generated events is not the order manager (author) but
    #     the teacher.
    #
    #     """
    #     if self.teacher:
    #         return self.teacher.get_as_user() or self.user
    #     return self.user

    def suggest_cal_guests(self, event):
        """Look up enrolments of this order and suggest them as guests."""
        # logger.info("20140314 suggest_guests")
        Enrolment = rt.models.orders.Enrolment
        qs = Enrolment.objects.filter(order=self).order_by('id')
        for obj in qs:
            # if obj.is_guest_for(event):
            g = obj.make_guest_for(event)
            if g is not None:
                yield g

    def before_auto_event_save(self, event):
        """
        Set room and start_time/end_time for automatic events.
        """
        assert not settings.SITE.loading_from_dump
        assert event.owner == self
        event.order = self
        event.room = self.journal.room
        event.start_time = self.start_time
        event.end_time = self.end_time
        super(Order, self).before_auto_event_save(event)

    @dd.displayfield(_("Calendar entries"))
    def events_text(self, ar=None):
        return ', '.join([
            day_and_month(e.start_date)
            for e in self.events_by_order().order_by('start_date')])

    def events_by_order(self, **kwargs):
        ct = rt.models.contenttypes.ContentType.objects.get_for_model(
            self.__class__)
        kwargs.update(owner_type=ct, owner_id=self.id)
        return rt.models.cal.Event.objects.filter(**kwargs)

    @dd.requestfield(_("Enrolments"))
    def enrolments(self, ar):
        return self.get_enrolments()

    def get_enrolments(self, **pv):
        return rt.models.orders.EnrolmentsByOrder.request(
            self, param_values=pv)

    # @dd.virtualfield(dd.HtmlBox(_("Presences")))
    # def presences_box(self, ar):
    #     # not finished
    #     if ar is None:
    #         return ''
    #     pv = ar.param_values
    #     # if not pv.start_date or not pv.end_date:
    #     #     return ''
    #     events = self.events_by_order().order_by('start_date')
    #     events = rt.models.system.PeriodEvents.started.add_filter(events, pv)
    #     return "TODO: copy logic from presence_sheet.wk.html"



# customize fields coming from mixins to override their inherited
# default verbose_names
# dd.update_field(Order, 'every_unit', default=models.NOT_PROVIDED)
# dd.update_field(Order, 'every', default=models.NOT_PROVIDED)


# ENROLMENT



class Enrolment(dd.Model):
    # invoiceable_date_field = 'request_date'
    # workflow_state_field = 'state'
    allow_cascaded_copy = 'order'
    allow_cascaded_delete = 'order'

    class Meta:
        app_label = 'orders'
        abstract = dd.is_abstract_model(__name__, 'Enrolment')
        verbose_name = _("Enrolment")
        verbose_name_plural = _('Enrolments')
        unique_together = ('order', 'worker')

    # order_layout = OrderLayouts.field(blank=True, editable=False)

    quick_search_fields = worker_name_fields

    #~ teacher = dd.ForeignKey(Teacher)
    order = dd.ForeignKey('orders.Order', related_name="enrolments_by_order")
    worker = dd.ForeignKey(worker_model, related_name="enrolments_by_worker")
    guest_role = dd.ForeignKey("cal.GuestRole", blank=True, null=True,
                               verbose_name=_("Role in calendar entries"))
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    @dd.chooser()
    def worker_choices(cls, order):
        return order.get_worker_choices()

    # def create_worker_choice(self, text):
    #     """
    #     Called when an unknown worker name was given.
    #     Try to auto-create it.
    #     """
    #     worker = dd.resolve_model(worker_model)
    #     kw = parse_name(text)
    #     if len(kw) != 2:
    #         raise ValidationError(
    #             "Cannot find first and last names in %r to \
    #             auto-create worker", text)
    #     p = worker(**kw)
    #     p.full_clean()
    #     p.save()
    #     return p

    def get_overview_elems(self, ar):
        if self.order_id:
            return [self.order.obj2href(ar)]
        return [self.obj2href(ar)]

    def get_guest_role(self):
        return self.guest_role

    def make_guest_for(self, event):
        gr = self.get_guest_role()
        if gr is not None:
            return rt.models.cal.Guest(
                        event=event,
                        partner=self.worker,
                        role=gr)

    def __str__(self):
        return "%s / %s" % (self.order, self.worker)

    def get_print_language(self):
        return self.worker.language

    def get_body_template(self):
        """Overrides :meth:`lino.core.model.Model.get_body_template`."""
        return self.order.body_template

    def get_excerpt_title(self):
        return self.order.get_excerpt_title()

dd.update_field(
    Enrolment, 'overview',
    verbose_name=Order._meta.verbose_name)

dd.update_field(Enrolment, 'order', blank=True)

@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`
    if not sender.is_installed('memo'):
        return

    Order = sender.models.orders.Order

    def cmd(parser, s):

        pk = s
        txt = None

        ar = parser.context['ar']
        kw = dict()
        # dd.logger.info("20161019 %s", ar.renderer)
        pk = int(pk)
        obj = Order.objects.get(pk=pk)
        # try:
        # except model.DoesNotExist:
        #     return "[{} {}]".format(name, s)
        if txt is None:
            txt = "{0}".format(obj.name)
            kw.update(title=obj.name)
        e = ar.obj2html(obj, txt, **kw)
        # return str(ar)
        return tostring(e)

    sender.plugins.memo.parser.register_django_model(
        'order', Order,
        cmd=cmd,
        # title=lambda obj: obj.name
    )

# class OrderItem(ProductDocItem, SequencedVoucherItem):
class OrderItem(SequencedVoucherItem):
    class Meta:
        app_label = 'orders'
        abstract = dd.is_abstract_model(__name__, 'OrderItem')
        verbose_name = _("Order item")
        verbose_name_plural = _("Order items")

    allow_cascaded_delete = 'voucher'

    voucher = dd.ForeignKey('orders.Order', related_name='items')
    # title = models.CharField(_("Heading"), max_length=200, blank=True)
    product = dd.ForeignKey('products.Product', blank=True, null=True)
    qty = dd.QuantityField(_("Quantity"), blank=True, null=True)
    # unit_price = dd.PriceField(_("Unit price"), blank=True, null=True)
    remark = models.CharField(_("Remark"), max_length=200, blank=True)



dd.inject_field('ledger.Journal', 'room', dd.ForeignKey('cal.Room', blank=True, null=True))

from .ui import *
