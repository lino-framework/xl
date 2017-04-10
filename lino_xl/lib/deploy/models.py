# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""Database models for this plugin.

"""

from __future__ import unicode_literals

from django.db import models

from lino.api import dd, rt, _

from lino.mixins import Sequenced, DatePeriod

from lino_xl.lib.excerpts.mixins import Certifiable
from lino.modlib.users.mixins import UserAuthored

from lino_xl.lib.tickets.models import site_model
from lino_xl.lib.clocking.mixins import Workable

class WishTypes(dd.ChoiceList):
    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("Wish type")
    verbose_name_plural = _("Wish types")

add = WishTypes.add_item
add('10', _("Agenda item"), "talk") # Tagesordnungspunkt
# add('20', _("Requirement"), "requirement")  # Anforderung
add('20', _("New feature"), "new_feature")
add('22', _("Optimization"), "optimization")
add('25', _("Bugfix"), "bugfix")
add('30', _("Gimmick"), "gimmick")  # ungefragtes Gimmick
add('40', _("Side effect"), "side_effect")  # Nebeneffekt
add('50', _("Resolution"), "todo")  # Vorsatz
add('60', _("Aftermath"), "aftermath")  # Nachwehe

# add('30', _("Observed"), "observed")



# @dd.python_2_unicode_compatible
# class Milestone(UserAuthored, DatePeriod, Certifiable):
#     """A **Milestone** is a named step of evolution on a given Site.  In
#     Scrum they are called sprints.

#     .. attribute:: closed

#        Closed milestones are hidden in most lists.

#     """
#     class Meta:
#         app_label = 'deploy'
#         # verbose_name = _("Sprint")
#         # verbose_name_plural = _('Sprints')
#         verbose_name = _("Milestone")
#         verbose_name_plural = _('Milestones')

#     site_field_name = 'site'
    
#     project = dd.ForeignKey(
#         'tickets.Project',
#         related_name='milestones_by_project', blank=True, null=True)
#     site = dd.ForeignKey(
#         site_model,
#         related_name='milestones_by_site', blank=True, null=True)
#     label = models.CharField(_("Label"), max_length=20, blank=True)
#     expected = models.DateField(_("Expected for"), blank=True, null=True)
#     reached = models.DateField(_("Reached"), blank=True, null=True)
#     description = dd.RichTextField(
#         _("Description"), blank=True, format="plain")
#     changes_since = models.DateField(
#         _("Changes since"), blank=True, null=True,
#         help_text=_("In printed document include a list of "
#                     "other changes since this date"))
#     closed = models.BooleanField(_("Closed"), default=False)

#     #~ def __unicode__(self):
#         #~ return self.label

#     def __str__(self):
#         label = self.label
#         if not label:
#             if self.reached:
#                 label = self.reached.isoformat()
#             else:
#                 label = "#{0}".format(self.id)
#         # return "{0}@{1}".format(label, self.project or self.site)
#         return "{0}@{1}".format(label, self.site)

#     @classmethod
#     def quick_search_filter(cls, search_text, prefix=''):
#         """Overrides the default behaviour defined in
#         :meth:`lino.core.model.Model.quick_search_filter`. For
#         milestones, when quick-searching for a text containing only
#         digits, the user usually means the :attr:`label` and *not* the
#         primary key.

#         """
#         if search_text.isdigit():
#             return models.Q(**{prefix+'label__contains': search_text})
#         return super(Milestone, cls).quick_search_filter(search_text, prefix)

    


@dd.python_2_unicode_compatible
class Deployment(Sequenced, Workable):
    class Meta:
        app_label = 'deploy'
        verbose_name = _("Wish")
        verbose_name_plural = _('Wishes')

    allow_cascaded_copy = 'milestone'
    
    ticket = dd.ForeignKey(
        'tickets.Ticket', related_name="deployments_by_ticket")
    milestone = dd.ForeignKey(
        dd.plugins.tickets.milestone_model,
        related_name="wishes_by_milestone")
    remark = dd.RichTextField(_("Remark"), blank=True, format="plain")
    # remark = models.CharField(_("Remark"), blank=True, max_length=250)
    wish_type = WishTypes.field(blank=True, null=True)

    def get_ticket(self):
        return self.ticket
    
    def get_siblings(self):
        "Overrides :meth:`lino.mixins.Sequenced.get_siblings`"
        qs = self.__class__.objects.filter(
                milestone=self.milestone).order_by('seqno')
        # print(20170321, qs)
        return qs
    
    @dd.chooser()
    def unused_milestone_choices(cls, ticket):
        # if not ticket:
        #     return []
        # if ticket.site:
        #     return ticket.site.milestones_by_site.all()
        qs = rt.models.deploy.Milestone.objects.filter(closed=False)
        qs = qs.order_by('label')
        return qs

    def __str__(self):
        return "{}@{}".format(self.seqno, self.milestone)



from lino.modlib.system.choicelists import (ObservedEvent)
from lino_xl.lib.tickets.choicelists import TicketEvents, T24, combine


class TicketEventToDo(ObservedEvent):
    text = _("To do")

    def add_filter(self, qs, pv):
        if pv.start_date:
            pass
        if pv.end_date:
            qs = qs.exclude(
                deployment__milestone__end_date__lte=combine(
                    pv.end_date, T24))
        return qs


TicketEvents.add_item_instance(TicketEventToDo('todo'))


    
