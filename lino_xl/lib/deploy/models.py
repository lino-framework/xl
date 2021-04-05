# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Database models for this plugin.

"""

from django.db import models

from lino.api import dd, rt, _

from lino.mixins import Sequenced, DateRange
from lino.utils import join_elems
from lino.utils.instantiator import create_row
from etgen.html import E

from lino_xl.lib.excerpts.mixins import Certifiable
from lino.modlib.users.mixins import UserAuthored

from lino_xl.lib.tickets.models import Ticket, SpawnTicket
from lino_xl.lib.tickets.choicelists import TicketStates, LinkTypes
from lino_xl.lib.working.mixins import Workable
from lino_xl.lib.votes.choicelists import VoteStates
from django.contrib.contenttypes.models import ContentType


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



#
# class Milestone(UserAuthored, DateRange, Certifiable):
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


if False:  # broke after changes for #3621. If we want it back, I'd rather write
           # a new action from scratch instead of inheriting.

  class SpawnTicketFromWish(SpawnTicket):
    # label = _("Spawn new ticket")
    # label = "\u2611" "☑"
    # "\u2687"
    # icon_name = 'calendar'
    show_in_workflow = True
    show_in_bbar = False
    goto_new = False

    parameters = dict(
        summary=Ticket._meta.get_field('summary'),
        # just get_field fails with choser error
        enduser=dd.ForeignKey(
            Ticket._meta.get_field('end_user').remote_field.model,
            verbose_name=_("End user"), blank=True,),
        # Rich Editor doesn't work all the time...
        # Seems to work better with basic editor
        description=Ticket._meta.get_field('description')
    )

    class SpawnTicketLayout(dd.ActionParamsLayout):
        simple = dd.Panel("""summary
        enduser""")
        main = dd.Panel("""simple
        description""", height=50)
        window_size = (50,30)
    params_layout = SpawnTicketLayout()

    def action_param_defaults(self,ar, obj, **kw):
        kw = super(SpawnTicket, self).action_param_defaults(ar, obj, **kw)
        return kw

    def get_parent_ticket(self, ar):
        wish = ar.selected_rows[0]
        return wish.ticket

    def spawn_ticket(self, ar, p):
        t = rt.models.tickets.Ticket(
            user=ar.get_user(),
            summary=ar.action_param_values.summary,
            description=ar.action_param_values.description)
        return t

    def make_link(self, ar, new, old):
        wish = ar.selected_rows[0]

        d = wish.duplicate.run_from_code(ar)
        d.ticket = new
        d.milestone = wish.milestone
        d.wish_type = None
        d.remark = ""
        d.full_clean()
        d.save()
        super(SpawnTicketFromWish, self).make_link(ar, new, old)



class Deployment(Sequenced, Workable):
    class Meta:
        app_label = 'deploy'
        verbose_name = _("Wish")
        verbose_name_plural = _('Wishes')

    # SpawnTicket = SpawnTicketFromWish(_("New Ticket"), LinkTypes.triggers)

    allow_cascaded_copy = 'milestone'
    ticket = dd.ForeignKey(
        'tickets.Ticket', related_name="deployments_by_ticket")
    milestone = dd.ForeignKey(
        dd.plugins.tickets.milestone_model,
        related_name="wishes_by_milestone")
    remark = dd.RichTextField(_("Remark"), blank=True, format="plain")
    # remark = models.CharField(_("Remark"), blank=True, max_length=250)
    wish_type = WishTypes.field(blank=True, null=True)
    old_ticket_state = TicketStates.field(
        blank=True, null=True, verbose_name=_("Ticket State"))
    new_ticket_state = TicketStates.field(
        blank=True, null=True, verbose_name=_("New Ticket State"))
    deferred_to = dd.ForeignKey(
        dd.plugins.tickets.milestone_model,
        verbose_name=_("Deferred to"),
        blank=True, null=True,
        related_name="wishes_by_deferred")

    def get_ticket(self):
        return self.ticket

    def get_siblings(self):
        "Overrides :meth:`lino.mixins.Sequenced.get_siblings`"
        qs = self.__class__.objects.filter(milestone=self.milestone)
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

    def full_clean(self):
        super(Deployment, self).full_clean()
        if self.deferred_to:
            if self.milestone == self.deferred_to:
                raise Warning(_("Cannot defer to myself"))
            qs = rt.models.deploy.Deployment.objects.filter(
                milestone=self.deferred_to, ticket=self.ticket)
            if qs.count() == 0:
                create_row(
                    Deployment, milestone=self.deferred_to,
                    ticket=self.ticket, wish_type=self.wish_type,
                    remark=self.remark)


    def milestone_changed(self, ar):
        self.ticket_changed(ar)

    def ticket_changed(self, ar):
        if self.ticket is not None and self.milestone is not None:
            self.milestone.add_child_stars(self.milestone, self.ticket)

    def after_ui_create(self, ar):
        # print "Create"
        self.ticket_changed(ar)
        super(Deployment, self).after_ui_create(ar)


    # def after_ui_save(self, ar, cw):
    #     """
    #     Automatically invite every participant to vote on every wish when adding deployment.
    #     """
    #     super(Deployment, self).after_ui_save(ar, cw)
    #     self.milestone.after_ui_save(ar, cw)

    @dd.displayfield(_("Actions"))
    def workflow_buttons(self, ar, **kwargs):
        if ar is None:
            return ''
        l = super(Deployment, self).get_workflow_buttons(ar)

        sar = rt.models.comments.CommentsByRFC.insert_action.request_from(ar)

        owner = ContentType.objects.get(app_label='tickets', model="ticket")
        # sar.bound_action.icon_name = None
        # sar.bound_action.label = _(" New Comment")

        sar.known_values.update(
            owner_id=self.ticket.id,
            owner_type=owner,
            # owner=self.ticket,
            user=ar.get_user()
        )
        if sar.get_permission():
            l.append(E.span(u", "))
            l.append(sar.ar2button(icon_name=None, label=_("New Comment")))
        # print self.E.tostring(l)
        return l

    # @dd.displayfield(_("Assigned"))
    # def assigned_voters(self, ar):
    #     if ar is None:
    #         return None
    #     qs = rt.models.votes.Vote.objects.filter(
    #         votable=self.ticket, state=VoteStates.assigned)
    #     elems = [vote.user.obj2href(ar) for vote in qs]
    #     return E.p(*join_elems(elems, sep=', '))


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
