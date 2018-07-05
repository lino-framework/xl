# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Luc Saffre
# License: BSD (see file COPYING for details)

"""Database models for this plugin.

A **Project** is something into which somebody (the `partner`) invests
time, energy and money.  The partner can be either external or the
runner of the site.  Projects form a tree: each Project can have a
`parent` (another Project for which it is a sub-project).

A **Ticket** is a concrete question or problem formulated by a a user.
A Ticket is always related to one and only one Project.  It may be
related to other tickets which may belong to other projects.

Projects are handled by their *name* while Tickets are handled by
their *number*.

"""

from __future__ import unicode_literals
from builtins import str

from django.conf import settings
from django.db import models
from django.db.models import Q

from lino import mixins
from lino.api import dd, rt, _

from etgen.html import E

from lino_xl.lib.cal.mixins import daterange_text
from lino.modlib.users.mixins import My
from lino.utils import join_elems

from .choicelists import TicketEvents, ProjectEvents, TicketStates, LinkTypes, Priorities

from .roles import TicketsReader, Reporter, Searcher, Triager, TicketsStaff

site_model = dd.plugins.tickets.site_model
milestone_model = dd.plugins.tickets.milestone_model


end_user_model = dd.plugins.tickets.end_user_model
# if dd.is_installed('tickets'):
#     site_model = dd.plugins.tickets.site_model
# else:
#     site_model = None
    

class ProjectTypes(dd.Table):
    required_roles = dd.login_required(TicketsStaff)
    model = 'tickets.ProjectType'
    column_names = 'name *'
    detail_layout = """id name
    ProjectsByType
    """


class TicketTypes(dd.Table):
    required_roles = dd.login_required(TicketsStaff)
    model = 'tickets.TicketType'
    column_names = 'name reporting_type *'
    detail_layout = """id name reporting_type
    TicketsByType
    """


class ProjectDetail(dd.DetailLayout):
    main = "general #deploy.DeploymentsByProject more"

    general = dd.Panel("""
    ref name
    description #CompetencesByProject
    """, label=_("General"))

    more = dd.Panel("""
    parent type reporting_type
    company assign_to #contact_person #contact_role private closed
    start_date end_date srcref_url_template changeset_url_template
    ProjectsByParent #deploy.MilestonesByProject
    # cal.EntriesByProject
    """, label=_("More"))


class Projects(dd.Table):
    required_roles = dd.login_required(Reporter)
    model = 'tickets.Project'
    detail_layout = ProjectDetail()
    column_names = "ref name parent company private *"
    order_by = ["ref"]
    parameters = mixins.ObservedDateRange(
        observed_event=ProjectEvents.field(blank=True),
        interesting_for=dd.ForeignKey(
            'contacts.Partner',
            verbose_name=_("Interesting for"),
            blank=True, null=True,
            help_text=_("Only projects interesting for this partner.")))
    params_layout = """interesting_for start_date end_date observed_event"""

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Projects, self).get_request_queryset(ar)
        pv = ar.param_values

        if pv.observed_event:
            qs = pv.observed_event.add_filter(qs, pv)

        if pv.interesting_for:
            qs = qs.filter(
                Q(company=pv.interesting_for))
            
        if False:  # pv.interesting_for:
            qs = qs.filter(
                Q(tickets_by_project__site__partner=pv.interesting_for) |
                Q(tickets_by_project__site__partner__isnull=True))
            interests = pv.interesting_for.interests_by_partner.values(
                'topic')
            if len(interests) > 0:
                qs = qs.filter(
                    tickets_by_project__topic__in=interests,
                    tickets_by_project__private=False)
        return qs


class AllProjects(Projects):
    required_roles = dd.login_required(TicketsStaff)


# class ActiveProjects(Projects):
#     """Show a list of active projects.

#     For an example, see :ref:`noi.specs.projects`.

#     """
#     label = _("Active projects")
#     column_names = 'ref name start_date activity_overview *'
#     required_roles = dd.login_required(Triager)

#     @classmethod
#     def param_defaults(self, ar, **kw):
#         kw = super(ActiveProjects, self).param_defaults(ar, **kw)
#         kw.update(start_date=dd.demo_date())
#         kw.update(end_date=dd.demo_date())
#         kw.update(observed_event=ProjectEvents.active)
#         return kw


class ProjectsByParent(Projects):
    master_key = 'parent'
    label = _("Subprojects")
    column_names = "ref name children_summary *"


class TopLevelProjects(Projects):
    label = _("Projects (tree)")
    required_roles = dd.login_required(TicketsStaff)
    column_names = 'ref name parent children_summary *'
    filter = Q(parent__isnull=True)
    variable_row_height = True


class ProjectsByType(Projects):
    master_key = 'type'
    column_names = "ref name *"


class ProjectsByCompany(Projects):
    master_key = 'company'
    column_names = "ref name *"


class ProjectsByPerson(Projects):
    master_key = 'contact_person'
    column_names = "ref name *"


# class Competences(dd.Table):
#     required_roles = dd.login_required(TicketsUser)
#     model = 'tickets.Competence'
#     order_by = ['-priority', 'project__ref']

#     detail_layout = """
#     project user priority 
#     remark
#     TicketsByCompetence:40 deploy.MilestonesByCompetence:20 #deploy.DeploymentsByCompetence 
#     """

    # detail_layout = dd.DetailLayout("""
    # project user priority 
    # TicketsByCompetence
    # """, window_size=(40, 'auto'))

# class AllCompetences(Competences):
#     required_roles = dd.login_required(TicketsStaff)
    
# class MyCompetences(My, Competences):
#     label = _("My projects")
#     column_names = 'priority overview #project remark *'
#     # column_names = 'priority project tickets_overview *'
#     params_panel_hidden = True
#     # editable = False
#     display_mode = "html"  # (doesn't work) TODO #1594 
    
#     insert_layout = """
#     project 
#     priority 
#     remark
#     """

# class CompetencesByProject(Competences):
#     master_key = 'project'
#     order_by = ["user__username"]
#     column_names = 'user workflow_buttons:30 *'
    
#     insert_layout = """
#     user
#     priority 
#     remark
#     """

if False:
    
    class Wishes(dd.Table):
        model = 'tickets.Wish'
        required_roles = dd.login_required(Reporter)

        insert_layout = """
        ticket 
        project
        priority 
        """

    class AllWishes(Wishes):
        required_roles = dd.login_required(TicketsStaff)


    class WishesByProject(Wishes):
        master_key = 'project'
        order_by = ["priority"]
        column_names = 'priority ticket remark *'
        insert_layout = None



    class WishesByTicket(Wishes):
        master_key = 'ticket'
        order_by = ["project__ref"]
        column_names = 'project *'
        insert_layout = """
        project
        remark
        """

        display_mode = "summary"

        @classmethod
        def get_table_summary(self, obj, ar):
            """The summary view for this table.

            Implements :meth:`lino.core.actors.Actor.get_table_summary`.

            """
            sar = self.request_from(ar, master_instance=obj)
            chunks = []
            items = [o.obj2href(ar) for o in sar]
            if len(items) > 0:
                chunks += join_elems(items, ", ")
            sar = self.insert_action.request_from(sar)
            if sar.get_permission():
                chunks.append(sar.ar2button())
            return E.p(*chunks)



# class MyWishes(My, Wishes):
#     order_by = ["priority"]
#     column_names = 'priority ticket project workflow_buttons:30 *'
#     # @classmethod
#     # def setup_request(self, ar):
#     #     u = ar.get_user()
#     #     if u.person:
#     #         qs = rt.models.contacts.Role.objects.filter(person=u.person)
#     #         if qs.count() == 1:
#     #             ar.master_instance = qs[0].company
#     #     super(MyWishes, self).setup_request(ar)
    

    


class Links(dd.Table):
    model = 'tickets.Link'
    required_roles = dd.login_required(TicketsStaff)
    stay_in_grid = True
    detail_layout = dd.DetailLayout("""
    parent
    type
    child
    """, window_size=(40, 'auto'))


class LinksByTicket(Links):
    label = _("Dependencies")
    required_roles = dd.login_required(Triager)
    master = 'tickets.Ticket'
    column_names = 'parent type_as_parent:10 child'
    display_mode = 'summary'

    @classmethod
    def get_request_queryset(self, ar):
        mi = ar.master_instance  # a Person
        if mi is None:
            return
        Link = rt.models.tickets.Link
        flt = Q(parent=mi) | Q(child=mi)
        return Link.objects.filter(flt).order_by(
            'child__modified', 'parent__modified')

    @classmethod
    def get_table_summary(self, obj, ar):
        """The :meth:`summary view <lino.core.actors.Actor.get_table_summary>`
        for :class:`LinksByTicket`.

        """
        # if obj.pk is None:
        #     return ''
        #     raise Exception("20150218")
        sar = self.request_from(ar, master_instance=obj)
        links = []
        for lnk in sar:
            if lnk.parent is None or lnk.child is None:
                pass
            else:
                if lnk.child_id == obj.id:
                    i = (lnk.type.as_child(), lnk.parent)
                else:
                    i = (lnk.type.as_parent(), lnk.child)
                links.append(i)

        def by_age(a):
            return a[1].modified

        try:
            links.sort(key=by_age)
        # except AttributeError:
        except (AttributeError, ValueError):
            # AttributeError: 'str' object has no attribute 'as_date'
            # possible when empty birth_date
            # ValueError: day is out of range for month
            pass

        tbt = dict()  # tickets by lnktype
        for lnktype, other in links:
            lst = tbt.setdefault(lnktype, [])
            # txt = "#%d" % other.id
            lst.append(other.obj2href(ar))

        items = []
        for lnktype, lst in tbt.items():
            items.append(E.li(unicode(lnktype), ": ", *join_elems(lst, ', ')))
        elems = []
        if len(items) > 0:
            # elems += join_elems(items)
            # elems.append(l(*items))
            elems.append(E.ul(*items))
        # else:
        #     elems.append(_("No dependencies."))

        # Buttons for creating relationships:

        sar = obj.spawn_triggered.request_from(ar)
        if ar.renderer.is_interactive and sar.get_permission():
            btn = sar.ar2button(obj)
            elems += [E.br(), btn]

        if self.insert_action is not None and ar.renderer.is_interactive:
            sar = self.insert_action.request_from(ar)
            if sar.get_permission():
                actions = []
                for lt in LinkTypes.objects():
                    actions.append(E.br())
                    sar.known_values.update(type=lt, parent=obj)
                    sar.known_values.pop('child', None)
                    btn = sar.ar2button(None, lt.as_parent(), icon_name=None)
                    if not lt.symmetric:
                        # actions.append('/')
                        sar.known_values.update(type=lt, child=obj)
                        sar.known_values.pop('parent', None)
                        btn2 = sar.ar2button(None, lt.as_child(), icon_name=None)
                        # actions.append(btn)
                        btn = E.span(btn, '/', btn2)
                    actions.append(btn)
                    # actions.append(' ')
                # actions = join_elems(actions, E.br)

                if len(actions) > 0:
                    elems += [E.br(), _("Create dependency as ")] + actions
        return E.div(*elems)


class TicketDetail(dd.DetailLayout):
    main = "general more history_tab"

    general = dd.Panel("""
    general1 #WishesByTicket
    comments.CommentsByRFC:60 working.SessionsByTicket:20
    """, label=_("General"))

    history_tab = dd.Panel("""
    changes.ChangesByMaster:50 #stars.StarsByController:20
    """, label=_("History"), required_roles=dd.login_required(Triager))

    general1 = """
    summary:40 id:6 user:12 end_user:12
    site topic project private
    workflow_buttons #assigned_to waiting_for
    """

    more = dd.Panel("""
    more1 DuplicatesByTicket:20
    description:40 upgrade_notes:20 LinksByTicket:20
    """, label=_("More"))

    more1 = """
    #nickname:10     created modified reported_for #fixed_for ticket_type:10
    state ref duplicate_of planned_time priority
    # standby feedback closed
    """


class Tickets(dd.Table):
    """Global list of all tickets.

    .. attribute:: site

        Select a site if you want to see only tickets for this site.

    .. attribute:: show_private

        Show only (or hide) tickets that are marked private.

    .. attribute:: show_todo

        Show only (or hide) tickets which are todo (i.e. state is New
        or ToDo).

    .. attribute:: show_active

        Show only (or hide) tickets which are active (i.e. state is Talk
        or ToDo).

    .. attribute:: show_assigned

        Show only (or hide) tickets that are assigned to somebody.

    .. attribute:: has_site

        Show only (or hide) tickets which have a site assigned.

    .. attribute:: feasable_by

        Show only tickets for which the given supplier is competent.

    """
    required_roles = dd.login_required(Searcher)
    # label = _("All tickets")
    # required_roles = set()  # also for anonymous
    model = 'tickets.Ticket'
    order_by = ["-id"]
    column_names = 'id summary:50 user:10 topic #faculty ' \
                   'workflow_buttons:30 #site:10 project:10 *' # Site commented to not disturbe care
    detail_layout = 'tickets.TicketDetail'
    insert_layout = """
    summary
    end_user
    """
    # insert_layout = dd.InsertLayout("""
    # # reporter #product
    # summary
    # description
    # """, window_size=(70, 20))

    detail_html_template = "tickets/Ticket/detail.html"

    parameters = mixins.ObservedDateRange(
        observed_event=TicketEvents.field(blank=True),
        topic=dd.ForeignKey('topics.Topic', blank=True, ),
        site=dd.ForeignKey(site_model, blank=True),
        end_user=dd.ForeignKey(
            end_user_model,
            verbose_name=_("End user"),
            blank=True, null=True,
            help_text=_("Only rows concerning this end user.")),
        assigned_to=dd.ForeignKey(
            end_user_model,
            # settings.SITE.user_model,
            verbose_name=_("Assigned_to"),
            blank=True, null=True,
            help_text=_("Only tickets with this user assigned.")),
        not_assigned_to=dd.ForeignKey(
            end_user_model,
            # settings.SITE.user_model,
            verbose_name=_("Not assigned to"),
            blank=True, null=True,
            help_text=_("Only that this user is not assigned to.")),
        interesting_for=dd.ForeignKey(
            'contacts.Partner',
            verbose_name=_("Interesting for"),
            blank=True, null=True,
            help_text=_("Only tickets interesting for this partner.")),
        deployed_to=dd.ForeignKey(
            milestone_model,
            blank=True, null=True),
        project=dd.ForeignKey(
            'tickets.Project',
            blank=True, null=True),
        state=TicketStates.field(
            blank=True,
            help_text=_("Only rows having this state.")),
        priority=Priorities.field(_("Priority"),
            blank=True,
            help_text=_("Only rows having this priority.")),
        show_assigned=dd.YesNo.field(_("Assigned"), blank=True),
        show_deployed=dd.YesNo.field(
            _("Deployed"), blank=True,
            help_text=_("Whether to show tickets with at "
                        "least one deployment")),
        show_active=dd.YesNo.field(_("Active"), blank=True),
        show_todo=dd.YesNo.field(_("To do"), blank=True),
        has_site=dd.YesNo.field(_("Has site"), blank=True),
        show_private=dd.YesNo.field(_("Private"), blank=True),
        has_ref=dd.YesNo.field(_("Has reference"), blank=True)
    )

    params_layout = """
    user end_user assigned_to not_assigned_to interesting_for site state priority deployed_to
    #has_site show_assigned show_active show_deployed show_todo show_private
    start_date end_date observed_event topic has_ref"""

    # simple_parameters = ('reporter', 'assigned_to', 'state', 'project')

    @classmethod
    def get_simple_parameters(cls):
        for p in super(Tickets, cls).get_simple_parameters():
            yield p
        yield 'end_user'
        yield 'state'
        yield 'project'
        yield 'topic'
        yield 'site'
        yield 'priority'
        if not dd.is_installed('votes'):
            yield 'assigned_to'

    @classmethod
    def get_queryset(self, ar, **filter):
        return self.model.objects.select_related(
            'user', 'assigned_to', 'project',
            'duplicate_of', 'end_user')
        
    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Tickets, self).get_request_queryset(ar)
        pv = ar.param_values

        if pv.observed_event:
            qs = pv.observed_event.add_filter(qs, pv)

        if pv.interesting_for:
            qs = qs.filter(
                Q(site__company=pv.interesting_for))
                # Q(votes_by_ticket__project__company=pv.interesting_for))
            
        # if pv.project:
        #     qs = qs.filter(
        #         Q(votes_by_ticket__project=pv.project))
            
        if False:  # pv.interesting_for:

            interests = pv.interesting_for.interests_by_partner.values(
                'topic')
            if len(interests) > 0:
                qs = qs.filter(
                    Q(site__partner=pv.interesting_for) |
                    Q(topic__in=interests, private=False))

        # if pv.show_closed == dd.YesNo.no:
        #     qs = qs.filter(closed=False)
        # elif pv.show_closed == dd.YesNo.yes:
        #     qs = qs.filter(closed=True)

        if dd.is_installed('votes'):
            if pv.assigned_to:
                # qs = qs.filter(
                #     Q(votes_by_ticket__user=pv.assigned_to) |
                #     Q(votes_by_ticket__end_user=pv.assigned_to)).distinct()
                qs = qs.filter(
                    votes_by_ticket__user=pv.assigned_to).distinct()
            
            if pv.not_assigned_to:
                # print(20170318, self, qs.model, pv.not_assigned_to)
                # qs = qs.exclude(
                #     Q(votes_by_ticket__user_id=pv.not_assigned_to.id) |
                #     Q(votes_by_ticket__end_user_id=pv.not_assigned_to.id))
                qs = qs.exclude(
                    votes_by_ticket__user=pv.not_assigned_to)
            if pv.show_assigned == dd.YesNo.no:
                qs = qs.filter(vote__isnull=False).distinct()
            elif pv.show_assigned == dd.YesNo.yes:
                qs = qs.filter(vote__isnull=True).distinct()

        else:
            # NB: assigned_to is a simple parameter field
            if pv.not_assigned_to:
                qs = qs.exclude(assigned_to=pv.not_assigned_to)

            if pv.show_assigned == dd.YesNo.no:
                qs = qs.filter(assigned_to__isnull=False)
            elif pv.show_assigned == dd.YesNo.yes:
                qs = qs.filter(assigned_to__isnull=True)
            
        if pv.deployed_to:
            # qs = qs.filter(
            #     Q(votes_by_ticket__user=pv.assigned_to) |
            #     Q(votes_by_ticket__end_user=pv.assigned_to)).distinct()
            qs = qs.filter(
                deployments_by_ticket__milestone=pv.deployed_to).distinct()
        if pv.show_deployed == dd.YesNo.no:
            qs = qs.exclude(deployments_by_ticket__isnull=False)
        elif pv.show_deployed == dd.YesNo.yes:
            qs = qs.filter(deployments_by_ticket__isnull=False)

        active_states = TicketStates.filter(active=True)
        if pv.show_active == dd.YesNo.no:
            qs = qs.exclude(state__in=active_states)
        elif pv.show_active == dd.YesNo.yes:
            qs = qs.filter(state__in=active_states)

        todo_states = TicketStates.filter(show_in_todo=True)
        if pv.show_todo == dd.YesNo.no:
            qs = qs.exclude(state__in=todo_states)
        elif pv.show_todo == dd.YesNo.yes:
            qs = qs.filter(state__in=todo_states)

        if pv.has_site == dd.YesNo.no:
            # qs = qs.filter(votes_by_ticket__project__isnull=True)
            qs = qs.filter(site__isnull=True)
        elif pv.has_site == dd.YesNo.yes:
            # qs = qs.filter(votes_by_ticket__project__isnull=False)
            qs = qs.filter(site__isnull=False)

        # if pv.show_standby == dd.YesNo.no:
        #     qs = qs.filter(standby=False)
        # elif pv.show_standby == dd.YesNo.yes:
        #     qs = qs.filter(standby=True)

        if pv.show_private == dd.YesNo.no:
            qs = qs.filter(
                private=False, project__private=False)
        elif pv.show_private == dd.YesNo.yes:
            qs = qs.filter(
                Q(private=True) |
                Q(project__private=True))

        if pv.has_ref == dd.YesNo.yes:
            qs = qs.filter(ref__isnull=False)
        elif pv.has_ref == dd.YesNo.no:
            qs = qs.filter(ref__isnull=True)
        # print 20150512, qs.query
        # 1253
        
        # the following caused a RuntimeWarning and was useless since
        # the same filter is applied by
        # pv.observed_event.add_filter(qs, pv) above: if
        # pv.start_date: qs = qs.filter(created__gte=pv.start_date) if
        # pv.end_date: qs = qs.filter(created__lte=pv.end_date)

        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Tickets, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.start_date or pv.end_date:
            yield daterange_text(
                pv.start_date,
                pv.end_date)


class AllTickets(Tickets):
    label = _("All tickets")
    use_paging = True
    required_roles = dd.login_required(Searcher)


class DuplicatesByTicket(Tickets):
    """Shows the tickets which are marked as duplicates of this
    (i.e. whose `duplicate_of` field points to this ticket.

    """
    display_mode = 'html'
    label = _("Duplicates")
    master_key = 'duplicate_of'
    column_names = "overview state *"
    editable = False
    required_roles = set([])



class RefTickets(Tickets):
    """
    Tickets that have a reference.
    """
    label = _("Reference Tickets")
    required_roles = dd.login_required(Triager)

    column_names = 'id ref:20 summary:50 user:10 site:10 ' \
                   'workflow_buttons:30 *'
    order_by = ["ref"]
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(RefTickets, self).param_defaults(ar, **kw)
        kw.update(
            has_ref=dd.YesNo.yes
        )
        return kw

class UnassignedTickets(Tickets):
    if dd.is_installed('votes'):
        column_names = "summary project user votes_by_ticket *"
    else:
        column_names = "summary project user assigned_to *"
        
    label = _("Unassigned Tickets")
    required_roles = dd.login_required(Triager)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(UnassignedTickets, self).param_defaults(ar, **kw)
        kw.update(show_assigned=dd.YesNo.no)
        # kw.update(show_private=dd.YesNo.no)
        # kw.update(show_active=dd.YesNo.yes)
        # kw.update(show_closed=dd.YesNo.no)
        kw.update(state=TicketStates.opened)
        return kw



class TicketsByEndUser(Tickets):
    master_key = 'end_user'
    column_names = ("overview:50 workflow_buttons * ")
    # display_mode = "summary"
    required_roles = dd.login_required(TicketsReader)

    @classmethod
    def get_table_summary(self, obj, ar):
        """The :meth:`summary view <lino.core.actors.Actor.get_table_summary>`
        for this table.

        """
        sar = self.request_from(ar, master_instance=obj)

        chunks = []
        items = [o.obj2href(ar) for o in sar]
        if len(items) > 0:
            chunks += join_elems(items, ", ")
            
        sar = self.insert_action.request_from(sar)
        if sar.get_permission():
            chunks.append(sar.ar2button())

        return E.p(*chunks)


    


class TicketsByType(Tickets):
    master_key = 'ticket_type'
    column_names = "summary state  *"


class TicketsByTopic(Tickets):
    master_key = 'topic'
    column_names = "summary state  *"


class PublicTickets(Tickets):
    label = _("Public tickets")
    order_by = ["-id"]
    column_names = 'overview:50 ticket_type:10 site:10 *'
    # filter = Q(assigned_to=None)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(PublicTickets, self).param_defaults(ar, **kw)
        # kw.update(show_assigned=dd.YesNo.no)
        kw.update(show_private=dd.YesNo.no)
        # kw.update(show_active=dd.YesNo.yes)
        # kw.update(show_closed=dd.YesNo.no)
        kw.update(state=TicketStates.opened)
        return kw


class TicketsToTriage(Tickets):
    """List of tickets that need to be triaged.  Currently this is
    equivalent to those having their state set to :attr:`new
    <lino_xl.lib.tickets.choicelists.TicketStates.new>`.

    """
    label = _("Tickets to triage")
    required_roles = dd.login_required(Triager)
    button_label = _("Triage")
    order_by = "priority -id".split()
    column_names = 'overview:50 priority topic:10 #user:10 ' \
                   '#assigned_to:10 ticket_type:10 workflow_buttons:40 *'
    params_panel_hidden = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(TicketsToTriage, self).param_defaults(ar, **kw)
        kw.update(state=TicketStates.new)
        return kw

    welcome_message_when_count = 0


class TicketsToTalk(Tickets):
    label = _("Tickets to talk")
    required_roles = dd.login_required(Triager)
    order_by = ["priority", "-deadline", "-id"]
    # order_by = ["-id"]
    column_names = "overview:50 priority #deadline waiting_for " \
                   "workflow_buttons:40 *"

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(TicketsToTalk, self).param_defaults(ar, **kw)
        kw.update(state=TicketStates.talk)
        return kw


# class TicketsToDo(Tickets):
#     """Shows a list of tickets "to do". This means attributed to me and
#     in an active state.

#     """
#     label = _("Tickets to do")
#     required_roles = dd.login_required()
#     order_by = ["-priority", "-deadline", "-id"]
#     column_names = 'overview:50 priority deadline user end_user ' \
#                    'workflow_buttons:40 *'
#     params_layout = """
#     user end_user assigned_to site project state 
#     start_date end_date observed_event topic feasable_by"""

#     @classmethod
#     def param_defaults(self, ar, **kw):
#         kw = super(TicketsToDo, self).param_defaults(ar, **kw)
#         # kw.update(state=TicketStates.todo)
#         kw.update(show_todo=dd.YesNo.yes)
#         kw.update(assigned_to=ar.get_user())
#         return kw


class ActiveTickets(Tickets):
    """Show all tickets that are in an active state.

    """
    label = _("Active tickets")
    required_roles = dd.login_required(Triager)
    order_by = ["-id"]
    # order_by = ["-modified", "id"]
    column_names = 'overview:50 priority site ' \
                   'assigned_to:10 ticket_type:10 workflow_buttons:40 *'

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(ActiveTickets, self).param_defaults(ar, **kw)
        kw.update(show_active=dd.YesNo.yes)
        # kw.update(show_closed=dd.YesNo.no)
        # kw.update(show_standby=dd.YesNo.no)
        return kw

class MyTickets(My, Tickets):
    """Show all active tickets reported by me."""
    label = _("My tickets")
    required_roles = dd.login_required(Reporter)
    order_by = ["priority", "-id"]
    column_names = ("priority overview:50 workflow_buttons *")
    params_layout = """
    user end_user site project state
    start_date end_date observed_event topic show_active"""
    params_panel_hidden = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyTickets, self).param_defaults(ar, **kw)
        kw.update(show_active=dd.YesNo.yes)
        # kw.update(show_closed=dd.YesNo.no)
        # kw.update(show_standby=dd.YesNo.no)
        return kw

class TicketsSummary(Tickets):
    order_by = ["state", "priority", "-id"]
    display_mode = 'summary'

    @classmethod
    def get_table_summary(self, master, ar):
        # master is None when called on a master table.
        if master is None:
            sar = ar
        else:
            sar = self.request_from(ar, master_instance=master)
            
        # every element of `items` is a tuple `(state,
        # list-of-objects)`.  in ar are ordered by state. we just group
        # them 
        items = []
        ci = None
            
        for obj in sar:  # self.get_request_queryset(ar):
            btn = obj.obj2href(ar)
            if ci is not None and ci[0] is obj.state:
                ci[1].append(btn)
            else:
                ci = (obj.state, [btn])
                items.append(ci)

        # now render them as a UL containing on LI per item
        items = [E.li(str(i[0]), ' : ', *join_elems(i[1], ", "))
                 for i in items]

        return E.ul(*items)

class MyTicketsToWork(TicketsSummary):
    """Show all active tickets assigned to me."""
    label = _("Tickets to work")
    required_roles = dd.login_required(Reporter)
    column_names = 'overview:50 workflow_buttons:30 *'
    params_layout = """
    user end_user site project state
    start_date end_date observed_event topic show_active"""
    params_panel_hidden = True

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyTicketsToWork, self).param_defaults(ar, **kw)
        kw.update(show_active=dd.YesNo.yes)
        # kw.update(show_todo=dd.YesNo.yes)
        kw.update(assigned_to=ar.get_user())
        return kw



# class InterestingTickets(ActiveTickets):
#     label = _("Interesting tickets")

#     @classmethod
#     def param_defaults(self, ar, **kw):
#         kw = super(InterestingTickets, self).param_defaults(ar, **kw)
#         # kw.update(interesting_for=ar.get_user())
#         return kw


# class TicketsByPartner(Tickets):
#     master_key = 'partner'
#     column_names = "summary project user *"


class TicketsFixed(Tickets):
    label = _("Fixed tickets")
    master_key = 'fixed_for'
    column_names = "id summary user *"
    editable = False


class TicketsReported(Tickets):
    label = _("Reported tickets")
    master_key = 'reported_for'
    column_names = "id summary user *"
    editable = False


class TicketsByReporter(Tickets):
    label = _("Reported tickets ")
    master_key = 'user'
    column_names = "id summary:60 workflow_buttons:20 *"


class SiteDetail(dd.DetailLayout):
    bottom_left = """
    description
    tickets.SubscriptionsBySite
    """
    bottom = """
        bottom_left:30 TicketsBySite
        """
    general = dd.Panel("""
        id name 
        company contact_person reporting_type
        workflow_buttons:1 remark
        bottom""", label=_("General"))
    main = """general meetings.MeetingsBySite"""


class Subscriptions(dd.Table):
    required_roles = dd.login_required(Reporter)
    model = 'tickets.Subscription'
    
class SubscriptionsBySite(Subscriptions):
    master_key = 'site'
    column_names = 'user primary'
    
class SubscriptionsByUser(Subscriptions):
    master_key = 'user'
    column_names = 'site primary'
    
class Sites(dd.Table):
    # required_roles = set()  # also for anonymous
    required_roles = dd.login_required(Reporter)
    model = 'tickets.Site'
    column_names = "name company contact_person remark workflow_buttons id *"
    order_by = ['name']
    # detail_html_template = "tickets/Site/detail.html"
    parameters = dd.ParameterPanel(
        watcher=dd.ForeignKey('users.User', blank=True, null=True, )
    )

    insert_layout = """
    name
    remark
    description
    """
    detail_layout = 'tickets.SiteDetail'

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Sites, self).get_request_queryset(ar)
        pv = ar.param_values

        if pv.watcher:
            sqs = rt.models.tickets.Subscription.objects.filter(user=pv.watcher)
            subscribed_sites = sqs.values_list('site')
            qs = qs.filter(pk__in=subscribed_sites)

        return qs




class MySites(Sites):
    label = _("My Sites")

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MySites, self).param_defaults(ar, **kw)
        kw.update(watcher=ar.get_user())
        return kw

def get_summary_columns():
    for ts in TicketStates.get_list_items():
        if ts.active:
            k = ts.get_summary_field()
            if k is not None:
                yield k
    

class MySitesDashboard(MySites):
    label = _("Sites Overview")

    @classmethod
    def setup_columns(cls):
        cls.column_names = "overview "
        cls.column_names += ' '.join(get_summary_columns())

class AllSites(Sites):
    required_roles = dd.login_required(TicketsStaff)

# # List of sites that user X has stared?
# class SitesByPartner(Sites):
#     master_key = 'partner'
#     column_names = "name remark *"


class TicketsBySite(TicketsSummary):
    # label = _("Known problems")
    master_key = 'site'
    column_names = ("priority overview:50 workflow_buttons *")
    # order_by = ["priority", "-id"]

    @classmethod
    def param_defaults(self, ar, **kw):
        # mi = ar.master_instance
        kw = super(TicketsBySite, self).param_defaults(ar, **kw)
        kw.update(show_active=dd.YesNo.yes)
        # kw.update(interesting_for=mi.partner)
        # kw.update(end_date=dd.today())
        # kw.update(observed_event=TicketEvents.todo)
        return kw

# class TicketsByProject(Tickets):
#     master_key = 'project'
#     required_roles = dd.login_required(Triager)
#     column_names = ("priority overview:50 workflow_buttons *")
#     order_by = ["priority", "-id"]


#     @classmethod
#     def param_defaults(self, ar, **kw):
#         kw = super(TicketsByProject, self).param_defaults(ar, **kw)
#         # mi = ar.master_instance
#         # if mi is None or mi.project is None:
#         #     return kw
#         # print("20170318 master instance is", mi)
#         # kw.update(not_assigned_to=mi)
#         # kw.update(deployed_to=mi.project)
#         # kw.update(show_assigned=dd.YesNo.no)
#         kw.update(show_active=dd.YesNo.yes)
#         return kw
    
# class TicketsByCompetence(TicketsByProject):
#     master = 'tickets.Competence'
#     master_key = None
#     # required_roles = dd.login_required(Triager)
#     # column_names = ("overview:50 workflow_buttons upgrade_notes *")
#     display_mode = "html"

#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         # print("20170316 {}".format(ar.master_instance))
#         # kw.update(votes_by_ticket__project=ar.master_instance.project)
#         if ar.master_instance is not None:
#             kw.update(project=ar.master_instance.project)
#         return kw
    

# class MyKnownProblems(Tickets):
#     """For users whose `user_site` is set, show the known problems on
#     their site.

#     """
#     required_roles = dd.login_required()
#     label = _("My known problems")
#     abstract = not dd.is_installed('contacts')

#     # @classmethod
#     # def get_master_instance(self, ar, model, pk):
#     #     u = ar.get_user()
#     #     return u.user_site

#     @classmethod
#     def get_request_queryset(self, ar):
#         u = ar.get_user()
#         # print "20150910", u.user_site
#         if not u.user_site:
#             ar.no_data_text = _("Only for users whose `user_site` is set.")
#             return self.model.objects.none()
#         return super(MyKnownProblems, self).get_request_queryset(ar)

#     @classmethod
#     def param_defaults(self, ar, **kw):
#         u = ar.get_user()
#         kw = super(MyKnownProblems, self).param_defaults(ar, **kw)
#         if u.user_site:
#             kw.update(interesting_for=u.user_site.partner)
#         kw.update(end_date=dd.demo_date())
#         kw.update(observed_event=TicketEvents.todo)
#         return kw

#     @classmethod
#     def get_welcome_messages(cls, ar, **kw):
#         sar = ar.spawn(cls)
#         count = sar.get_total_count()
#         if count > 0:
#             msg = _("There are {0} known problems for {1}.")
#             msg = msg.format(count, ar.get_user().user_site)
#             yield ar.href_to_request(sar, msg)





