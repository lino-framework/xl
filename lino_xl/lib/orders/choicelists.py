# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function


from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd

# class OrderState(dd.State):
#     is_editable = True
#     is_exposed = True
#     is_invoiceable = True
#     auto_update_calendar = False
#
# class OrderStates(dd.Workflow):
#     item_class = OrderState
#     required_roles = dd.login_required(dd.SiteAdmin)
#     is_exposed = models.BooleanField(_("Exposed"), default=True)
#     is_invoiceable = models.BooleanField(_("Invoiceable"), default=True)
#     is_editable = models.BooleanField(_("Editable"), default=True)
#     auto_update_calendar = models.BooleanField(
#         _("Update calendar"), default=False)
#     column_names = "value name text is_exposed is_editable is_invoiceable auto_update_calendar"
#
# add = OrderStates.add_item
# add('10', _("Draft"), 'draft',
#     is_editable=True, is_invoiceable=False, is_exposed=True)
# add('20', _("Started"), 'active',
#     is_editable=False, is_invoiceable=True, is_exposed=True)
# add('30', _("Inactive"), 'inactive',
#     is_editable=False, is_invoiceable=False, is_exposed=False)
# add('40', _("Closed"), 'closed',
#     is_editable=False, is_invoiceable=False, is_exposed=False)
#
#
# class OrderArea(dd.Choice):
#     # force_guest_states = False
#     orders_table = 'orders.Orders'
#
#     def __init__(
#             self, value, text, name,
#             orders_table='orders.Orders', **kwargs):
#         self.orders_table = orders_table
#         super(OrderArea, self).__init__(value, text, name, **kwargs)
#
#
# class OrderAreas(dd.ChoiceList):
#     preferred_width = 10
#     verbose_name = _("Layout")
#     verbose_name_plural = _("Order layouts")
#     item_class = OrderArea
#     column_names = "value name text orders_table #force_guest_states"
#     required_roles = dd.login_required(dd.SiteAdmin)
#
#     @dd.virtualfield(models.CharField(_("Table")))
#     def orders_table(cls, choice, ar):
#         return str(choice.orders_table)
#
#
# add = OrderAreas.add_item
# try:
#     add('C', dd.plugins.orders.verbose_name, 'default')
# except AttributeError:
#     add('C', 'oops, orders not installed', 'default')
# # add('J', _("Journeys"), 'journeys')
#
#
