# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import logging
logger = logging.getLogger(__name__)

from decimal import Decimal
ZERO = Decimal()
ONE = Decimal(1)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.text import format_lazy

from lino.api import dd, rt, _
from lino import mixins

from lino.core.roles import Explorer
from lino.utils import join_elems
from etgen.html import E
from lino.utils.mti import get_child
from lino.utils.report import Report

from lino.modlib.system.choicelists import PeriodEvents
from lino.modlib.users.mixins import My

from lino_xl.lib.ledger.ui import ByJournal
from lino_xl.lib.ledger.choicelists import VoucherTypes

from .roles import OrdersUser, OrdersStaff

cal = dd.resolve_app('cal')

try:
    worker_model = dd.plugins.orders.worker_model
except AttributeError:
    # Happens only when Sphinx autodoc imports it and this module is
    # not installed.
    worker_model = 'foo.Bar'


class OrderDetail(dd.DetailLayout):
    required_roles = dd.login_required(OrdersUser)
    # start = "start_date start_time"
    # end = "end_date end_time"
    # freq = "every every_unit"
    # start end freq
    
    main = "general cal_tab enrolments"
    
    general = dd.Panel("""
    journal number start_date start_time end_time end_date
    workflow_buttons id:8 user
    name
    description
    """, label=_("General"))
    
    cal_tab = dd.Panel("""
    max_events max_date every_unit every
    monday tuesday wednesday thursday friday saturday sunday
    cal.EntriesByController
    """, label=_("Calendar"))

    enrolments_top = 'print_actions:15'

    enrolments = dd.Panel("""
    enrolments_top
    EnrolmentsByOrder
    """, label=_("Enrolments"))

# Order.detail_layout_class = OrderDetail

class Orders(dd.Table):
    # _order_area = None
    required_roles = dd.login_required(OrdersUser)
    model = 'orders.Order'
    detail_layout = 'orders.OrderDetail'
    insert_layout = """
    journal 
    name start_date
    """
    column_names = "start_date name workflow_buttons *"
    order_by = ['-start_date', '-start_time']
    auto_fit_column_widths = True

    # parameters = mixins.ObservedDateRange(
    #     worker=dd.ForeignKey(
    #         worker_model, blank=True, null=True),
    #     # user=dd.ForeignKey(
    #     #     settings.SITE.user_model,
    #     #     blank=True, null=True),
    #     show_exposed=dd.YesNo.field(
    #         _("Exposed"), blank=True,
    #         help_text=_("Whether to show rows in an exposed state"))
    # )
    #
    # params_layout = """user worker state
    # start_date end_date show_exposed"""

    # @classmethod
    # def get_actor_label(self):
    #     if self._order_area is not None:
    #         return self._order_area.text
    #     return super(Orders, self).get_actor_label()
    #
    # @classmethod
    # def get_simple_parameters(cls):
    #     s = list(super(Orders, cls).get_simple_parameters())
    #     s.append('worker')
    #     # s.append('state')
    #     # s.add('user')
    #     return s
    #
    # @classmethod
    # def get_request_queryset(self, ar, **kwargs):
    #     # dd.logger.info("20160223 %s", self)
    #     qs = super(Orders, self).get_request_queryset(ar, **kwargs)
    #     if isinstance(qs, list):
    #         return qs
    #
    #     if self._order_area is not None:
    #         qs = qs.filter(order_area=self._order_area)
    #
    #     pv = ar.param_values
    #     qs = PeriodEvents.active.add_filter(qs, pv)
    #
    #     qs = self.model.add_param_filter(
    #         qs, show_exposed=pv.show_exposed)
    #
    #     # if pv.start_date:
    #     #     # dd.logger.info("20160512 start_date is %r", pv.start_date)
    #     #     qs = PeriodEvents.started.add_filter(qs, pv)
    #     #     # qs = qs.filter(start_date__gte=pv.start_date)
    #     # if pv.end_date:
    #     #     qs = PeriodEvents.ended.add_filter(qs, pv)
    #     #     # qs = qs.filter(end_date__lte=pv.end_date)
    #     # dd.logger.info("20160512 %s", qs.query)
    #     return qs


class OrdersByJournal(Orders, ByJournal):
    # required_roles = dd.login_required(OrdersUser)
    # _order_area = OrderLayouts.default
    required_roles = dd.login_required(OrdersUser)
    master_key = 'journal'

    # orders_by_line = dd.ShowSlaveTable('orders.OrdersByLine')

VoucherTypes.add_item_lazy(OrdersByJournal)

class AllOrders(Orders):
    # _order_area = None
    required_roles = dd.login_required(Explorer)
    column_names = "journal number start_date:8 user " \
                   "weekdays_text:10 times_text:10 *"

class OrdersByPartner(Orders):
    master_key = 'partner'
    column_names = "start_date:8 journal number user " \
                   "weekdays_text:10 times_text:10 *"
    order_by = ['start_date']

class OrdersByRecipient(Orders):
    master_key = 'invoice_recipient'
    column_names = "partner start_date:8 journal number user " \
                   "weekdays_text:10 times_text:10 *"

class MyOrders(My, Orders):
    column_names = "start_date:8 name workflow_buttons *"
    order_by = ['start_date']
    
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyOrders, self).param_defaults(ar, **kw)
        # kw.update(state=OrderStates.active)
        kw.update(show_exposed=dd.YesNo.yes)
        return kw

# class EnrolmentDetail(dd.DetailLayout):
#     main = """
#     #request_date user start_date end_date
#     order worker
#     remark workflow_buttons
#     confirmation_details
#     """


class Enrolments(dd.Table):

    # _order_area = None

    required_roles = dd.login_required(OrdersUser)
    # debug_permissions=20130531
    model = 'orders.Enrolment'
    stay_in_grid = True
    # order_by = ['request_date']
    column_names = 'order order__state worker workflow_buttons user *'
    # hidden_columns = 'id state'
    insert_layout = """
    order
    worker
    remark
    """
    # detail_layout = "orders.EnrolmentDetail"

    # @classmethod
    # def get_title_tags(self, ar):
    #     for t in super(Enrolments, self).get_title_tags(ar):
    #         yield t
    #
    #     if ar.param_values.state:
    #         yield str(ar.param_values.state)
    #     elif not ar.param_values.participants_only:
    #         yield str(_("Also ")) + str(EnrolmentStates.cancelled.text)
    #     if ar.param_values.order_state:
    #         yield str(
    #             settings.SITE.models.orders.Order._meta.verbose_name) \
    #             + ' ' + str(ar.param_values.order_state)
    #     if ar.param_values.author:
    #         yield str(ar.param_values.author)


class AllEnrolments(Enrolments):
    required_roles = dd.login_required(Explorer)
    order_by = ['-id']
    column_names = 'id order worker worker__birth_date worker__age worker__country worker__city worker__gender *'


class EnrolmentsByWorker(Enrolments):
    params_panel_hidden = True
    required_roles = dd.login_required(OrdersUser)
    master_key = "worker"
    column_names = 'order remark workflow_buttons *'
    auto_fit_column_widths = True

    insert_layout = """
    # order_area
    order
    remark
    """

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(EnrolmentsByworker, self).param_defaults(ar, **kw)
        kw.update(participants_only=False)
        return kw

    # @classmethod
    # def get_actor_label(cls):
    #     if cls._order_area is not None:
    #         orders = cls._order_area.text
    #     else:
    #         orders = rt.models.orders.Order._meta.verbose_name_plural
    #     return format_lazy(
    #         _("{enrolments} in {orders}"),
    #         enrolments=rt.models.orders.Enrolment._meta.verbose_name_plural,
    #         orders=orders)

class EnrolmentsByOrder(Enrolments):
    params_panel_hidden = True
    required_roles = dd.login_required(OrdersUser)
    # required_roles = dd.login_required(OrdersUser)
    master_key = "order"
    column_names = 'worker guest_role' \
                   'remark workflow_buttons *'
    auto_fit_column_widths = True
    # cell_edit = False
    display_mode = 'html'

    insert_layout = """
    worker 
    guest_role
    remark
    """

    label = _("Workers")

    # @classmethod
    # def get_actor_label(self):
    #     return rt.models.orders.Enrolment._meta.verbose_name_plural


class OrderItemDetail(dd.DetailLayout):
    main = """
    seqno product discount
    unit_price qty total_base total_vat total_incl
    title
    description"""

    window_size = (80, 20)


class OrderItems(dd.Table):
    """Shows all order items."""
    model = 'orders.OrderItem'
    required_roles = dd.login_required(OrdersStaff)
    auto_fit_column_widths = True
    # hidden_columns = "seqno description total_base total_vat"

    detail_layout = 'orders.OrderItemDetail'

    insert_layout = """
    product discount qty
    title
    """

    stay_in_grid = True


class ItemsByOrder(OrderItems):
    label = _("Content")
    master_key = 'voucher'
    order_by = ["seqno"]
    required_roles = dd.login_required(OrdersUser)
    column_names = "product title discount unit_price qty total_incl *"


