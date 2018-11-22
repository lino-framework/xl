# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Desktop UI for this plugin.
"""

from __future__ import unicode_literals
from builtins import str

from lino import mixins

from etgen.html import E, tostring
from lino.utils import join_elems
from lino.modlib.users.mixins import My
from lino.api import dd, rt, _

# class MilestoneDetail(dd.DetailLayout):
#     main = """
#     left_box description
#     DeploymentsByMilestone
#     """
#     left_box = """
#     site project 
#     id label closed
#     # expected reached changes_since printed
#     """
    
# class Milestones(dd.Table):
#     """
#     .. attribute:: show_closed
#     """
#     order_by = ['-id']
#     # order_by = ['label', '-id']
#     model = 'deploy.Milestone'
#     stay_in_grid = True
#     detail_layout = MilestoneDetail()
#     insert_layout = dd.InsertLayout("""
#     site label
#     description
#     """, window_size=(50, 15))

#     parameters = mixins.ObservedDateRange(
#         show_closed=dd.YesNo.field(
#             blank=True, default=dd.YesNo.no.as_callable,
#             help_text=_("Show milestons which are closed.")))

#     params_layout = "user start_date end_date show_closed"
#     order_by = ['start_date', 'id']
#     column_names = "start_date site label user closed *"

#     @classmethod
#     def get_request_queryset(self, ar):
#         qs = super(Milestones, self).get_request_queryset(ar)
#         pv = ar.param_values
#         if pv.show_closed == dd.YesNo.no:
#             qs = qs.filter(closed=False)
#         elif pv.show_closed == dd.YesNo.yes:
#             qs = qs.filter(closed=True)
#         return qs

# class MyMilestones(My, Milestones):
#     column_names = "start_date overview closed *"
#     pass


# class MilestonesBySite(Milestones):
#     order_by = ['-start_date', '-label', '-id']
#     master_key = 'site'
#     # master_key = dd.plugins.tickets.milestone_model.site_field_name
#     column_names = "start_date label user expected reached closed id *"

# class MilestonesByProject(Milestones):
#     order_by = ['-start_date', '-label', '-id']
#     master_key = 'project'
#     column_names = "start_date label user expected reached closed *"


# class MilestonesByCompetence(MilestonesByProject):
#     master = 'tickets.Competence'
#     master_key = None

#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         if ar.master_instance is not None:
#             kw.update(project=ar.master_instance.project)
#         return kw
    

class Deployments(dd.Table):
    model = 'deploy.Deployment'
    parameters = mixins.ObservedDateRange(
        show_closed=dd.YesNo.field(
            blank=True, default=dd.YesNo.as_callable('no'),
            help_text=_("Show deployments on closed milestones.")))

    params_layout = "start_date end_date show_closed"
    stay_in_grid = True
    detail_layout = dd.DetailLayout("""
    milestone
    wish_type
    ticket
    remark
    """, window_size=(50, 15))


    @classmethod
    def unused_get_request_queryset(self, ar):
        qs = super(Deployments, self).get_request_queryset(ar)
        pv = ar.param_values
        cls = dd.plugins.tickets.milestone_model.workflow_state_field.choicelist
        closed = cls.filter(invoiceable=True)
        if pv.show_closed == dd.YesNo.no:
            qs = qs.filter(milestone__state__in=closed)
            # qs = qs.filter(milestone__closed=False)
        elif pv.show_closed == dd.YesNo.yes:
            qs = qs.exclude(milestone__state__in=closed)
            # qs = qs.filter(milestone__closed=True)
        return qs


class DeploymentsByMilestone(Deployments):
    # label = _("Deployed tickets")
    drag_drop_sequenced_field = 'seqno'
    order_by = ['seqno']
    master_key = 'milestone'
    column_names = "seqno move_buttons:8 ticket:30 old_ticket_state " \
                   "new_ticket_state wish_type remark:30 workflow_buttons *"
    preview_limit = 0
    insert_layout = dd.InsertLayout("""
    ticket
    remark
    """, window_size=(60, 15))
    


# class DeploymentsByProject(DeploymentsByMilestone):
#     master = 'tickets.Project'
#     master_key = None
#     display_mode = "html"

#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         # print("20170316 {}".format(ar.master_instance))
#         # kw.update(votes_by_ticket__project=ar.master_instance.project)
#         if ar.master_instance:
#             kw.update(milestone__project=ar.master_instance)
#         return kw
    

# class DeploymentsByCompetence(DeploymentsByProject):
#     master = 'tickets.Competence'
#     master_key = None
#     display_mode = "html"

#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         # print("20170316 {}".format(ar.master_instance))
#         # kw.update(votes_by_ticket__project=ar.master_instance.project)
#         mi = ar.master_instance
#         if mi and mi.project:
#             kw.update(milestone__project=mi.project)
#         return kw
    

class DeploymentsByTicket(Deployments):
    order_by = ['-milestone__end_date']
    master_key = 'ticket'
    # column_names = "milestone__reached milestone  remark *"
    column_names = "milestone wish_type remark *"
    insert_layout = dd.InsertLayout("""
    milestone wish_type
    remark
    """, window_size=(60, 15))
    
    display_mode = 'summary'
    stay_in_grid = True

    @classmethod
    def get_table_summary(cls, obj, ar):
        """Customized :meth:`summary view
        <lino.core.actors.Actor.get_table_summary>` for this table.

        """
        sar = cls.request_from(ar, master_instance=obj)
        html = []
        # items = [ar.obj2html(o, str(o.milestone)) for o in sar]
        qs = cls.model.objects.filter(ticket=obj)
        qs = dd.plugins.tickets.milestone_model.add_param_filter(
            qs, lookup_prefix='milestone__',
            # show_active=dd.YesNo.yes
            )
        items = E.ul()
        for o in qs:
            items.append(
                E.li(o.obj2href(ar, text=getattr(o.wish_type,'text', _("Wish"))), " in ", o.milestone.obj2href(ar), " : ", o.remark)
            )
        if len(items) > 0:
            html.append(tostring(items))
        # items = [o.milestone.obj2href(ar) for o in sar]
        sar = cls.insert_action.request_from(sar)
        if sar.get_permission():
            btn = sar.ar2button()
            html.append(btn)

        return ar.html_text(ar.parse_memo(tostring(html)))


    
