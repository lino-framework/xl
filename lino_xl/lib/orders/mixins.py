# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db.models import Q

from lino.api import dd, _
from .choicelists import EnrolmentStates


#
# class Enrollable(dd.Model):
#
#     class Meta(object):
#         abstract = True
#
#     def __str__(self):
#         s = self.get_full_name(salutation=False)
#         info = self.get_enrolment_info()
#         if info:
#             s += " ({0})".format(info)
#         return s
#
#     def get_enrolment_info(self):
#         """Return a short string with some additional information about this
#         worker.
#
#         """
#         return None
#
#     @classmethod
#     def setup_parameters(cls, fields):
#         fields.update(
#             enrolment_state=EnrolmentStates.field(
#                 blank=True, verbose_name=_("Enrolment state")),
#             order=dd.ForeignKey(
#                 'orders.Order', blank=True, null=True))
#
#         super(Enrollable, cls).setup_parameters(fields)
#
#
#     @classmethod
#     def get_request_queryset(cls, ar, **kwargs):
#         qs = super(Enrollable, cls).get_request_queryset(ar, **kwargs)
#         pv = ar.param_values
#         if pv.order:
#             qs = qs.filter(enrolments_by_worker__order=pv.order)
#             qs = qs.filter(
#                 Q(enrolments_by_worker__start_date__isnull=True) |
#                 Q(enrolments_by_worker__start_date__lte=dd.today()))
#             qs = qs.filter(
#                 Q(enrolments_by_worker__end_date__isnull=True) |
#                 Q(enrolments_by_worker__end_date__gte=dd.today()))
#             qs = qs.distinct()
#             # qs = qs.filter(enrolments_by_worker__order=pv.order)
#             # qs = qs.filter(
#             #     enrolments_by_worker__state__in=EnrolmentStates.filter(
#             #         invoiceable=True))
#             if not pv.enrolment_state:
#                 qs = qs.filter(
#                     enrolments_by_worker__state__in=EnrolmentStates.filter(
#                         invoiceable=True))
#                 # qs = qs.filter(
#                 #     enrolments_by_worker__state=EnrolmentStates.confirmed)
#         if pv.enrolment_state:
#             qs = qs.filter(enrolments_by_worker__state=pv.enrolment_state)
#             qs = qs.distinct()
#
#         return qs
#
#     @classmethod
#     def get_title_tags(self, ar):
#         for t in super(Enrollable, self).get_title_tags(ar):
#             yield t
#         pv = ar.param_values
#         if pv.order:
#             yield str(pv.order)
#         if pv.enrolment_state:
#             yield str(pv.enrolment_state)
#
