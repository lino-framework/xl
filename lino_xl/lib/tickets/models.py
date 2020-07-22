# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from rstgen.utils import py2url_txt
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericRelation
from etgen.html import tostring
from etgen.utils import join_elems, forcetext
from lino import mixins
from lino.api import dd, rt, _, pgettext, gettext
from lino.core.actions import CreateRow
from lino.core.utils import db2param
from lino.mixins.ref import Referrable
from lino.mixins.periods import DateRange
from lino.modlib.comments.mixins import Commentable, PrivateCommentsReader
from lino.modlib.notify.choicelists import MessageTypes
from lino.modlib.memo.mixins import rich_text_to_elems
from lino.modlib.uploads.mixins import UploadController
from lino.modlib.users.mixins import UserAuthored

from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.skills.mixins import Feasible
from lino_xl.lib.stars.mixins import Starrable
from lino_xl.lib.votes.choicelists import VoteStates
from lino_xl.lib.votes.mixins import Votable
from lino_xl.lib.working.choicelists import ReportingTypes
from lino_xl.lib.working.mixins import Workable
from .choicelists import TicketStates, LinkTypes, Priorities, SiteStates

MessageTypes.add_item('tickets', dd.plugins.tickets.verbose_name)

site_model = dd.plugins.tickets.site_model
milestone_model = dd.plugins.tickets.milestone_model
end_user_model = dd.plugins.tickets.end_user_model

# if dd.is_installed('tickets'):
#     site_model = dd.plugins.tickets.site_model
#     milestone_model = dd.plugins.tickets.milestone_model
# else:
#     site_model = None
#     milestone_model = None

class QuickAssignTo(dd.Action):
    """Quickly assign a ticket to another team member.
    """
    label = _("Assign to")
    icon_name = None
    show_in_bbar = False
    no_params_window = True
    parameters = dict(
        assign_to=dd.ForeignKey("users.User"),
        comment=models.CharField(_("Comment"), max_length=200, blank=True))

    params_layout = """
    assign_to
    comment
    """

    def get_action_permission(self, ar, obj, state):
        return not ar.get_user().is_anonymous

    def run_from_ui(self, ar, **kw):

        obj = ar.selected_rows[0]
        pv = ar.action_param_values
        obj.assigned_to = pv.assign_to
        obj.full_clean()
        obj.save()
        ar.success(refresh=True)



class Prioritized(dd.Model):
    class Meta:
        abstract = True
    #priority = models.SmallIntegerField(_("Priority"), default=100)
    priority = Priorities.field(default='normal')

class TimeInvestment(Commentable):
    class Meta:
        abstract = True

    closed = models.BooleanField(_("Closed"), default=False)

    planned_time = dd.DurationField(
        _("Planned time"),
        blank=True, null=True)

    # invested_time = models.TimeField(
    #     _("Invested time"), blank=True, null=True, editable=False)


# class ProjectType(mixins.BabelNamed):

#     class Meta:
#         app_label = 'tickets'
#         verbose_name = _("Project Type")
#         verbose_name_plural = _('Project Types')


class TicketType(mixins.BabelNamed):
    """The type of a :class:`Ticket`."""

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Ticket type")
        verbose_name_plural = _('Ticket types')

    reporting_type = ReportingTypes.field(blank=True)

# class Repository(UserAuthored):
#     class Meta:
#         verbose_name = _("Repository")
#         verbose_name_plural = _('Repositories')
#

#
# class Project(mixins.DateRange, TimeInvestment,
#               mixins.Hierarchical, mixins.Referrable,
#               ContactRelated):
#     class Meta:
#         app_label = 'tickets'
#         # verbose_name = _("Project")
#         # verbose_name_plural = _('Projects')
#         verbose_name = _("Mission")
#         verbose_name_plural = _('Missions')
#         abstract = dd.is_abstract_model(__name__, 'Project')


#     name = models.CharField(_("Name"), max_length=200)
#     # parent = dd.ForeignKey(
#     #     'self', blank=True, null=True, verbose_name=_("Parent"))
#     assign_to = dd.ForeignKey(
#         settings.SITE.user_model,
#         verbose_name=_("Assign tickets to"),
#         blank=True, null=True,
#         help_text=_("The user to whom new tickets will be assigned."))
#     type = dd.ForeignKey('tickets.ProjectType', blank=True, null=True)
#     description = dd.RichTextField(_("Description"), blank=True)
#     srcref_url_template = models.CharField(blank=True, max_length=200)
#     changeset_url_template = models.CharField(blank=True, max_length=200)
#     # root = dd.ForeignKey(
#     #     'self', blank=True, null=True, verbose_name=_("Root"))
#     reporting_type = ReportingTypes.field(blank=True)
#     # if dd.is_installed('working'):
#     #     reporting_type = ReportingTypes.field(blank=True)
#     # else:
#     #     reporting_type = dd.DummyField()
#     # milestone = dd.ForeignKey(
#     #     'deploy.Milestone',
#     #     related_name='projects_by_milestone', blank=True, null=True)

#     def __str__(self):
#         return self.ref or self.name

#     # @dd.displayfield(_("Activity overview"))
#     # def activity_overview(self, ar):
#     #     if ar is None:
#     #         return ''
#     #     TicketsByProject = rt.models.tickets.TicketsByProject
#     #     elems = []
#     #     for tst in (TicketStates.objects()):
#     #         pv = dict(state=tst)
#     #         sar = ar.spawn(
#     #             TicketsByProject, master_instance=self, param_values=pv)
#     #         num = sar.get_total_count()
#     #         if num > 0:
#     #             elems += [
#     #                 "{0}: ".format(tst.text),
#     #                 sar.ar2button(label=str(num))]
#     #     return E.p(*elems)

#     # def save(self, *args, **kwargs):
#     #     root = self.parent
#     #     while root is not None:
#     #         if root.parent is None:
#     #             break
#     #         else:
#     #             root = root.parent
#     #     self.root = root
#     #     super(Project, self).save(*args, **kwargs)



class Site(Referrable, ContactRelated, Starrable, DateRange):
    class Meta:
        app_label = 'tickets'
        verbose_name = pgettext("Ticketing", "Site")
        verbose_name_plural = pgettext("Ticketing", "Sites")
        abstract = dd.is_abstract_model(__name__, 'Site')

    ref_max_length = 20
    workflow_state_field = "state"

#     partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)
#     # responsible_user = dd.ForeignKey(
#     #     'users.User', verbose_name=_("Responsible"),
#     #     blank=True, null=True)
#     name = models.CharField(_("Designation"), max_length=200)
    child_starrables = [(milestone_model, 'site', None),
                        ('tickets.Ticket', 'site', None)]

    description = dd.RichTextField(_("Description"), blank=True)
    remark = models.CharField(_("Remark"), max_length=200, blank=True)
    name = models.CharField(
        _("Designation"), max_length=200, unique=True)
    reporting_type = ReportingTypes.field(blank=True)
    deadline = models.DateField(
        verbose_name=_("Deadline"),
        blank=True, null=True)

    state = SiteStates.field(default='draft')
    group = dd.ForeignKey('groups.Group', null=True, blank=True)
    hours_paid = dd.DurationField(_("Hours paid"), blank=True, null=True)
    private = models.BooleanField(_("Private"), default=False)

    def __str__(self):
        return self.ref or self.name

    #def get_change_observers(self, ar=None):
    #    for s in rt.models.tickets.Subscription.objects.filter(site=self):
    #        yield (s.user, s.user.mail_mode)

    def get_row_permission(self, ar, state, ba):
        """
        User has permission if:
        is tickets staff
        if a member of it's group
        is subscribed
        is contact person
        is contact person of org

        Currently only checks for is group member and role...
        """

        if not super(Site, self).get_row_permission(ar, state, ba):
            return False

        if ((self.group and self.group.members.filter(user__id=ar.get_user().id).count() == 0)
                and
                not ar.get_user().user_type.has_required_roles(
                    [TicketsStaff])):
            return False
        return True

    @classmethod
    def get_user_queryset(cls, user):
        qs = super(Site, cls).get_user_queryset(user)
        if user.is_anonymous:
            qs = qs.filter(private=False)
        elif not user.user_type.has_required_roles([TicketsStaff]):
            qs = qs.filter(Q(private=False) | Q(group__members__user=user)).distinct()
        return qs

    @classmethod
    def add_param_filter(
            cls, qs, lookup_prefix='', show_exposed=None, **kwargs):
        qs = super(Site, cls).add_param_filter(qs, **kwargs)
        exposed_states = SiteStates.filter(is_exposed=True)
        fkw = dict()
        fkw[lookup_prefix + 'state__in'] = exposed_states
        if show_exposed == dd.YesNo.no:
            qs = qs.exclude(**fkw)
        elif show_exposed == dd.YesNo.yes:
            qs = qs.filter(**fkw)
        return qs

    @dd.htmlbox(_("Description"))
    def parsed_description(self, ar):
        if ar is None:
            return ''
        html = ''
        if self.description:
            html += ar.parse_memo(self.description)
        return html

    def get_overview_elems(self, ar):
        elems = []
        if self.ref:
            txt = "{} {}".format(self.ref, self.name)
        else:
            txt = self.name
        elems.append(E.h2(txt))
        if self.description:
            elems += rich_text_to_elems(ar, self.description)
        return elems

Site.set_widget_options('hours_paid', width=6)
dd.update_field(Site, 'company', verbose_name=_("Client"))
dd.update_field(Site, 'contact_person', verbose_name=_("Contact person"))
# dd.update_field(Site, 'detail_link', verbose_name=_("Site"))


#
# class Competence(UserAuthored, Prioritized):

#     class Meta:
#         app_label = 'tickets'
#         verbose_name = _("Project membership")
#         verbose_name_plural = _("Project memberships")
#         unique_together = ['user', 'project']

#     project = dd.ForeignKey(
#         'tickets.Project', blank=True, null=True,
#         related_name="duties_by_project")
#     remark = models.CharField(_("Remark"), max_length=200, blank=True)
#     description = dd.DummyField()
#     # description = dd.RichTextField(_("Description"), blank=True)

#     def __str__(self):
#         if self.project and self.user:
#             return "{}/{}".format(
#                 self.user.username, self.project.ref)
#         return "{} #{}".format(self._meta.verbose_name, self.pk)

#     @dd.displayfield(_("Tickets overview"))
#     def tickets_overview(self, ar):
#         if ar is None:
#             return ''
#         me = ar.get_user()
#         Ticket = rt.models.tickets.Ticket
#         Vote = rt.models.votes.Vote
#         elems = []

#         tickets_by_state = OrderedDict()
#         for st in TicketStates.objects():
#             tickets_by_state[st] = set()
#         for t in Ticket.objects.filter(project=self.project):
#             # t = vote.votable
#             tickets_by_state[t.state].add(t)

#         items = []
#         for st, tickets in tickets_by_state.items():
#             if len(tickets) > 0:
#                 tickets = reversed(sorted(tickets))
#                 items.append(E.li(
#                     E.span("{} : ".format(st.button_text), title=str(st)),
#                     *join_elems([x.obj2href(ar) for x in tickets], ', ')
#                 ))
#         elems.append(E.ul(*items))
#         return E.p(*elems)


# class CloseTicket(dd.Action):
#     #label = _("Close ticket")
#     label = "\u2611"
#     help_text = _("Mark this ticket as closed.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is not None or obj.closed is not None:
#             return False
#         return super(CloseTicket, self).get_action_permission(ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         now = datetime.datetime.now()
#         for obj in ar.selected_rows:
#             obj.closed = now
#             obj.save()
#             ar.set_response(refresh=True)


# class StandbyTicket(dd.Action):
#     #label = _("Standby mode")
#     label = "\u2a37"
#     label = "\u2609"
#     help_text = _("Put this ticket into standby mode.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is not None or obj.closed is not None:
#             return False
#         return super(StandbyTicket, self).get_action_permission(
#             ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         now = datetime.datetime.now()
#         for obj in ar.selected_rows:
#             obj.standby = now
#             obj.save()
#             ar.set_response(refresh=True)


# class ActivateTicket(dd.Action):
#     # label = _("Activate")
#     label = "☀"  # "\u2600"
#     help_text = _("Reactivate this ticket from standby mode or closed state.")
#     show_in_workflow = True
#     show_in_bbar = False

#     def get_action_permission(self, ar, obj, state):
#         if obj.standby is None and obj.closed is None:
#             return False
#         return super(ActivateTicket, self).get_action_permission(
#             ar, obj, state)

#     def run_from_ui(self, ar, **kw):
#         for obj in ar.selected_rows:
#             obj.standby = False
#             obj.closed = False
#             obj.save()
#             ar.set_response(refresh=True)


class SpawnTicket(dd.Action):
    label = _("Spawn child ticket")
    # label = "\u2611" "☑"
    # label = "⚇"  # "\u2687"
    # show_in_workflow = False
    # show_in_bbar = False
    # goto_new = True
    params_layout = """
    link_type
    ticket_summary
    """

    parameters = dict(
        link_type=LinkTypes.field(default='requires'),
        ticket_summary=models.CharField(
            pgettext("Ticket", "Summary"), max_length=200,
            blank=False)
        )

    # def setup_parameters(self, params):
    #     super(SpawnTicket, self).setup_parameters(params)
    #     params.update(
    #         link_type=db2param('tickets.Link.type'),
    #         ticket_summary=db2param('tickets.Ticket.summary'))

    def run_from_ui(self, ar, **kw):
        pv = ar.action_param_values
        parent = ar.selected_rows[0]
        child = rt.models.tickets.Ticket(
            user=ar.get_user(),
            summary=pv.ticket_summary,
            site=parent.site)
        child.full_clean()
        child.save_new_instance(ar)
        link = rt.models.tickets.Link(
            parent=parent, child=child, type=pv.link_type)
        link.full_clean()
        link.save(force_insert=True)
        ar.goto_instance(child)
        ar.success()


class Ticket(UserAuthored, mixins.CreatedModified, TimeInvestment,
             Votable, Starrable, Workable, Prioritized, Feasible,
             UploadController, mixins.Referrable):
    quick_search_fields = "summary description ref"
    workflow_state_field = 'state'
    create_session_on_create = True
    disable_author_assign = False

    class Meta:
        app_label = 'tickets'
        verbose_name = _("Ticket")
        verbose_name_plural = _('Tickets')
        abstract = dd.is_abstract_model(__name__, 'Ticket')

    # project = dd.DummyField()
    # project = dd.ForeignKey(
    #     'tickets.Project', blank=True, null=True,
    #     related_name="tickets_by_project")
    site = dd.ForeignKey(site_model, blank=True, null=True,
                         related_name="tickets_by_site")
    # topic = dd.ForeignKey('topics.Topic', blank=True, null=True)
    # nickname = models.CharField(_("Nickname"), max_length=50, blank=True)

    private = models.BooleanField(_("Private"), default=False)

    summary = models.CharField(
        pgettext("Ticket", "Summary"), max_length=200,
        blank=False,
        help_text=_("Short summary of the problem."))
    description = dd.RichTextField(_("Description"), blank=True)
    upgrade_notes = dd.RichTextField(
        _("Resolution"), blank=True, format='plain')
    ticket_type = dd.ForeignKey(
        'tickets.TicketType', blank=True, null=True)
    duplicate_of = dd.ForeignKey(
        'self', blank=True, null=True, verbose_name=_("Duplicate of"),
        related_name="duplicated_tickets")

    end_user = dd.ForeignKey(
        end_user_model,
        verbose_name=_("End user"),
        blank=True, null=True,
        related_name="reported_tickets")
    state = TicketStates.field(default=TicketStates.as_callable('new'))
    # rating = Ratings.field(blank=True)
    deadline = models.DateField(
        verbose_name=_("Deadline"),
        blank=True, null=True)

    # deprecated fields:
    reported_for = dd.ForeignKey(
        milestone_model,
        related_name='tickets_reported',
        verbose_name='Reported for',
        blank=True, null=True,
        help_text=_("Milestone for which this ticket has been reported."))
    fixed_for = dd.ForeignKey(  # no longer used since 20150814
        milestone_model,
        related_name='tickets_fixed',
        verbose_name='Fixed for',
        blank=True, null=True,
        help_text=_("The milestone for which this ticket has been fixed."))
    reporter = dd.ForeignKey(
        settings.SITE.user_model,
        blank=True, null=True,
        verbose_name=_("Reporter"))
    waiting_for = models.CharField(
        _("Waiting for"), max_length=200, blank=True)
    feedback = models.BooleanField(
        _("Feedback"), default=False)
    standby = models.BooleanField(_("Standby"), default=False)

    # spawn_triggered = SpawnTicket(
    #     _("Spawn triggered ticket"),
    #     LinkTypes.triggers)
    # spawn_triggered = SpawnTicket("⚇", LinkTypes.triggers)  # "\u2687"
    spawn_ticket = SpawnTicket()  # "\u2687"

    fixed_since = models.DateTimeField(
        _("Fixed since"), blank=True, null=True, editable=False)
    # fixed_date = models.DateField(
    #     _("Fixed date"), blank=True, null=True)
    # fixed_time = models.TimeField(
    #     _("Fixed time"), blank=True, null=True)
    last_commenter = dd.ForeignKey(
        settings.SITE.user_model,
        related_name='tickets_last_commter',
        verbose_name=_("Commented Last"),
        blank=True, null=True,
        help_text=_("Last user to make a comment"))

    comments = GenericRelation('comments.Comment',
        content_type_field='owner_type', object_id_field='owner_id',
        related_query_name="ticket")

    quick_assign_to_action = QuickAssignTo()

    @dd.displayfield(_("Assign to"))
    def quick_assign_to(self, ar):
        if ar is None:
            return ''
        elems = []
        found_existing = False
        if self.site and self.site.group:
            for m in self.site.group.members.all():
                kw = dict(action_param_values=dict(assign_to=m.user))
                u = m.user
                label = u.initials or u.username or str(u.pk)
                if m.user == self.assigned_to:
                    elems.append(label)
                    found_existing = True
                else:
                    elems.append(ar.instance_action_button(
                        self.quick_assign_to_action, label=label, request_kwargs=kw))
        if self.assigned_to_id and not found_existing:
            u = self.assigned_to
            label = u.initials or u.username or str(u.pk)
            elems.append(label + "!")
            # ticket is assigned to a user who is not member of the team
        return E.p(*join_elems(elems, sep=", "))


    @classmethod
    def get_user_queryset(cls, user):
        qs = super(Ticket, cls).get_user_queryset(user)
        if user.is_anonymous:
            qs = qs.filter(private=False, site__private=False)
        elif not user.user_type.has_required_roles([TicketsStaff]):
            qs = qs.filter(
                Q(site__group__members__user__id=user.pk) |
                Q(user=user) | Q(end_user=user)|
                Q(assigned_to=user)|
                Q(private=False, site__private=False))
        return qs

    def is_comment_private(self, comment, ar):
        if self.site_id and self.site.private:
            return True
        return self.private

    @classmethod
    def get_comments_filter(cls, user):
        if user.is_anonymous:
            return super(Ticket, cls).get_comments_filter(user)
        if user.user_type.has_required_roles([PrivateCommentsReader]):
            return None
        flt = Q(ticket__site__group__members__user__id=user.pk)
        flt |= Q(ticket__user=user) | Q(ticket__end_user=user)
        flt |= Q(ticket__assigned_to=user)
        flt |= Q(user=user) | Q(private=False)
        return flt

    # @classmethod
    # def add_comments_filter(cls, qs, user):
    #     # note that this requires the related_query_name of the GenericRelation
    #     if user.is_anonymous:
    #         qs = qs.filter(ticket__private=False, ticket__site__private=False).distinct()
    #     elif not user.user_type.has_required_roles([TicketsStaff]):
    #         qs = qs.filter(
    #             Q(ticket__site__group__members__user__id=user.pk) |
    #             Q(ticket__user=user) | Q(ticket__end_user=user)|
    #             Q(ticket__assigned_to=user)|
    #             Q(ticket__private=False, ticket__site__private=False)).distinct()
    #         # print(20191125, qs.query)
    #     return qs

    def get_rfc_description(self, ar):
        html = ''
        _ = gettext
        if self.description:
            # html += tostring(E.b(_("Description")))
            html += ar.parse_memo(self.description)
        if self.upgrade_notes:
            html += tostring(E.b(_("Resolution"))) + ": "
            html += ar.parse_memo(self.upgrade_notes)
        if self.duplicate_of_id:
            html += tostring(_("Duplicate of")) + " "
            html += tostring(self.duplicate_of.obj2href(ar))
        return html

    def full_clean(self):
        if self.id and self.duplicate_of_id == self.id:
            self.duplicate_of = None
        # print "20150523b on_create", self.reporter
        if not self.site_id:
            person = self.end_user or self.user.get_person()
            qs = rt.models.tickets.Site.objects.filter(contact_person=person)
            qs = qs.filter(state=SiteStates.active)
            qs = qs.filter(Q(end_date__isnull=True) | Q(end_date__lte=dd.today()))
            qs = qs.order_by('-id')
            # qs = rt.models.tickets.Subscription.objects.filter(
            #     user=user, primary=True)
            if qs.count():
                # self.site = qs[0].site
                self.site = qs.first()
        super(Ticket, self).full_clean()

    def get_change_owner(self):
        if self.site_id is not None:
            return self.site.group or self.site

    def on_worked(self, session):
        """This is automatically called when a work session has been created
        or modified.

        """
        if self.fixed_since is None and session.is_fixing and session.end_time:
            self.fixed_since = session.get_datetime('end')

        self.touch()
        self.full_clean()
        self.save()

    def get_comment_group(self):
        return self.site

    def on_commented(self, comment, ar, cw):
        """This is automatically called when a comment has been created"""
        self.last_commenter = comment.user
        self.touch()
        self.save()

    # def get_project_for_vote(self, vote):
    #     if self.project:
    #         return self.project
    #     qs = rt.models.tickets.Competence.objects.filter(user=vote.user)
    #     qs = qs.order_by('priority')
    #     if qs.count() > 0:
    #         return qs[0].project
    #     return rt.models.tickets.Project.objects.all()[0]

    def obj2href(self, ar, **kwargs):
        kwargs.update(title=self.summary)
        return ar.obj2html(self, "#{}".format(self.id), **kwargs)

    def disabled_fields(self, ar):
        rv = super(Ticket, self).disabled_fields(ar)
        # if self.project and not self.project.private:
        #     rv.add('private')
        if not ar.get_user().user_type.has_required_roles([Triager]):
            rv.add('user')
            # rv.add('fixed_since')
            # rv.add('fixed_date')
            # rv.add('fixed_time')
        return rv

    # def get_choices_text(self, request, actor, field):
    #     return "{0} ({1})".format(self, self.summary)

    def __str__(self):
        # if self.nickname:
        #     return "#{0} ({1})".format(self.id, self.nickname)
        if False and self.state.button_text:
            return "#{0} ({1} {2})".format(
                self.id, self.state.button_text, self.summary)
        return "#{0} ({1} {2})".format(
            self.id, self.state.button_text, self.summary)

    @dd.chooser()
    def reported_for_choices(cls, site):
        if not site:
            return []
        # return site.milestones_by_site.filter(reached__isnull=False)
        return site.milestones_by_site.all()

    @dd.chooser()
    def fixed_for_choices(cls, site):
        if not site:
            return []
        return site.milestones_by_site.all()

    # @profile
    def get_overview_elems(self, ar):
        """Overrides :meth:`lino.core.model.Model.get_overview_elems`.
        """
        elems = [ar.obj2html(self)]  # show full summary
        # elems += [' ({})'.format(self.state.button_text)]
        # elems += [' ', self.state.button_text, ' ']
        if self.user and self.user != ar.get_user():
            elems += [' ', _(" by "), self.user.obj2href(ar)]
        if self.end_user_id:
            elems += [' ', _("for"), ' ', self.end_user.obj2href(ar)]

        if dd.is_installed('votes'):
            qs = rt.models.votes.Vote.objects.filter(
                votable=self, state=VoteStates.assigned)
            if qs.count() > 0:
                elems += [', ', _("assigned to"), ' ']
                elems += join_elems(
                    [vote.user.obj2href(ar) for vote in qs], sep=', ')
        elif getattr(self, "assigned_to", None):
            elems += [", ", _("assigned to"), " ", self.assigned_to.obj2href(ar)]

        return E.p(*forcetext(elems))
        # return E.p(*join_elems(elems, sep=', '))

        # if ar.actor.model is self.__class__:
        #     elems += [E.br(), _("{} state:").format(
        #         self._meta.verbose_name), ' ']
        #     elems += self.get_workflow_buttons(ar)
        # else:
        #     elems += [' (', str(self.state.button_text), ')']
        # return elems

    # def get_change_body(self, ar, cw):
    #     return tostring(E.p(
    #         _("{user} worked on [ticket {t}]").format(
    #             user=ar.get_user(), t=self.id)))

    def get_vote_raters(self):

        """"Yield the
        :meth:`lino_xl.lib.votes.mixins.Votable.get_vote_raters` for
        this ticket.  This is the author and (if set) the
        :attr:`end_user`.

        """
        if self.user:
            yield self.user
        if issubclass(
                settings.SITE.user_model,
                dd.resolve_model(end_user_model)):
            if self.end_user:
                u = self.end_user.get_as_user()
                if u is not None:
                    yield u

    def is_workable_for(self, user):
        if self.standby or self.closed:
            return False
        if not self.state.active and not user.user_type.has_required_roles(
                [Triager]):
            return False
        return True

    @classmethod
    def quick_search_filter(cls, search_text, prefix=''):
        """
        To skip mixins.Referrable quick_search_filter
        """
        return super(mixins.Referrable, cls).quick_search_filter(search_text, prefix)

# from django.contrib.contenttypes.fields import GenericRelation
# dd.inject_action('comments.Comment', ticket=GenericRelation(Ticket))


# dd.update_field(Ticket, 'user', verbose_name=_("Reporter"))



class Link(dd.Model):
    class Meta:
        app_label = 'tickets'
        verbose_name = _("Dependency")
        verbose_name_plural = _("Dependencies")

    allow_cascaded_delete = 'parent child'
    # when i delete a ticket that is child of another ticket, then Lino also
    # deletes the relationship with the ticket. But Lino does not allow me to
    # delete a ticket that is itself parent to one or more other tickets.

    type = LinkTypes.field(default='requires')
    parent = dd.ForeignKey(
        'tickets.Ticket',
        verbose_name=_("Parent"),
        related_name='tickets_children')
    child = dd.ForeignKey(
        'tickets.Ticket',
        blank=True, null=True,
        verbose_name=_("Child"),
        related_name='tickets_parents')

    @dd.displayfield(_("Type"))
    def type_as_parent(self, ar):
        # print('20140204 type_as_parent', self.type)
        return self.type.as_parent()

    @dd.displayfield(_("Type"))
    def type_as_child(self, ar):
        # print('20140204 type_as_child', self.type)
        return self.type.as_child()

    def __str__(self):
        if self.type is None:
            return "Link object"  # super(Link, self).__unicode__()
        return _("%(child)s is %(what)s") % dict(
            child=str(self.child),
            what=self.type_of_parent_text())

    def type_of_parent_text(self):
        return _("%(type)s of %(parent)s") % dict(
            parent=self.parent,
            type=self.type.as_child())


# dd.inject_field(
#     'users.User', 'project',
#     dd.ForeignKey(
#         'tickets.Project',
#         blank=True, null=True, related_name="users_by_project",
#         help_text=_("The project you are currently working on")))


@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`

    if not sender.is_installed('memo'):
        return

    Ticket = sender.models.tickets.Ticket
    mp = sender.plugins.memo.parser

    mp.register_django_model(
        'ticket', Ticket, title=lambda obj: obj.summary)
    mp.add_suggester(
        "#", sender.models.tickets.Ticket.objects.order_by('id'), 'id')

    def py2html(parser, s):
        url, txt = py2url_txt(s)
        if url:
            # lines = inspect.getsourcelines(s)
            return '<a href="{0}" target="_blank">{1}</a>'.format(url, txt)
        return "<pre>{}</pre>".format(s)

    mp.register_command('py', py2html)


from .ui import *
