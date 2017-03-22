# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Desktop UI for this plugin.
"""

from __future__ import unicode_literals
from builtins import str

from lino import mixins

from lino.utils.xmlgen.html import E
from lino.utils import join_elems
from lino.api import dd, rt, _

class MilestoneDetail(dd.DetailLayout):
    main = """
    left_box description
    DeploymentsByMilestone
    """
    left_box = """
    site project 
    id label 
    expected reached closed
    changes_since printed
    """
    
class Milestones(dd.Table):
    """
    .. attribute:: show_closed
    """
    order_by = ['-id']
    # order_by = ['label', '-id']
    model = 'deploy.Milestone'
    stay_in_grid = True
    detail_layout = MilestoneDetail()
    insert_layout = dd.InsertLayout("""
    site label
    description
    """, window_size=(50, 15))

    parameters = mixins.ObservedPeriod(
        show_closed=dd.YesNo.field(
            blank=True, default=dd.YesNo.no.as_callable,
            help_text=_("Show milestons which are closed.")))

    params_layout = "start_date end_date show_closed"

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Milestones, self).get_request_queryset(ar)
        pv = ar.param_values
        if pv.show_closed == dd.YesNo.no:
            qs = qs.filter(closed=False)
        elif pv.show_closed == dd.YesNo.yes:
            qs = qs.filter(closed=True)
        return qs


class MilestonesBySite(Milestones):
    order_by = ['-label', '-id']
    master_key = 'site'
    column_names = "label expected reached closed id *"

class MilestonesByProject(Milestones):
    order_by = ['-label', '-id']
    master_key = 'project'
    column_names = "label expected reached closed *"


class MilestonesByCompetence(MilestonesByProject):
    master = 'tickets.Competence'
    master_key = None

    @classmethod
    def get_filter_kw(self, ar, **kw):
        if ar.master_instance is not None:
            kw.update(project=ar.master_instance.project)
        return kw
    

class Deployments(dd.Table):
    model = 'deploy.Deployment'
    parameters = mixins.ObservedPeriod(
        show_closed=dd.YesNo.field(
            blank=True, default=dd.YesNo.no.as_callable,
            help_text=_("Show deployments on closed milestones.")))

    params_layout = "start_date end_date show_closed"
    stay_in_grid = True
    detail_layout = dd.DetailLayout("""
    milestone
    ticket
    remark
    """, window_size=(50, 'auto'))


    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Deployments, self).get_request_queryset(ar)
        pv = ar.param_values
        if pv.show_closed == dd.YesNo.no:
            qs = qs.filter(milestone__closed=False)
        elif pv.show_closed == dd.YesNo.yes:
            qs = qs.filter(milestone__closed=True)
        return qs


class DeploymentsByMilestone(Deployments):
    label = _("Deployed tickets")
    order_by = ['seqno']
    master_key = 'milestone'
    column_names = "seqno move_buttons:8 ticket:30 ticket__state:10 remark:30  *"
    insert_layout = dd.InsertLayout("""
    ticket
    remark
    """, window_size=(60, 10))
    


# class DeploymentsByProject(DeploymentsByMilestone):
#     master = 'tickets.Project'
#     master_key = None
#     slave_grid_format = "html"

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
#     slave_grid_format = "html"

#     @classmethod
#     def get_filter_kw(self, ar, **kw):
#         # print("20170316 {}".format(ar.master_instance))
#         # kw.update(votes_by_ticket__project=ar.master_instance.project)
#         mi = ar.master_instance
#         if mi and mi.project:
#             kw.update(milestone__project=mi.project)
#         return kw
    

class DeploymentsByTicket(Deployments):
    order_by = ['-milestone__label']
    master_key = 'ticket'
    # column_names = "milestone__reached milestone  remark *"
    column_names = "milestone remark *"
    insert_layout = dd.InsertLayout("""
    milestone
    remark
    """, window_size=(60, 10))
    
    slave_grid_format = 'summary'
    stay_in_grid = True

    @classmethod
    def get_slave_summary(cls, obj, ar):
        """Customized :meth:`summary view
        <lino.core.actors.Actor.get_slave_summary>` for this table.

        """
        sar = cls.request_from(ar, master_instance=obj)
        html = []
        items = [ar.obj2html(o, str(o.milestone)) for o in sar]
        sar = cls.insert_action.request_from(sar)
        if sar.get_permission():
            btn = sar.ar2button()
            items.append(btn)

        if len(items) > 0:
            html += join_elems(items, sep=', ')
            
        return E.p(*html)


    
