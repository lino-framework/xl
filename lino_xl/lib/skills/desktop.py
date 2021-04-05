# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
from __future__ import unicode_literals

from builtins import str

from django.db import models

from lino.api import dd, rt, _
from lino.modlib.users.mixins import My
from lino.modlib.users.desktop import Users
from etgen.html import E
from lino.utils import join_elems
from .roles import SkillsStaff

class SkillTypes(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = 'skills.SkillType'
    stay_in_grid = True
    detail_layout = """
    id name
    SkillsByType
    """
    insert_layout = """
    id
    name
    """

class Skills(dd.Table):
    model = 'skills.Skill'
    # order_by = ["ref", "name"]
    stay_in_grid = True
    detail_layout = """
    id name
    parent skill_type affinity
    SkillsByParent:40 remarks:40
    OffersBySkill DemandsBySkill
    """
    insert_layout = """
    name
    parent
    """


class AllSkills(Skills):
    label = _("Skills (all)")
    required_roles = dd.login_required(dd.SiteStaff)
    column_names = 'name parent skill_type remarks *'
    order_by = ["name"]


class TopLevelSkills(Skills):
    label = _("Skills (tree)")
    required_roles = dd.login_required(dd.SiteStaff)
    order_by = ["name"]
    column_names = 'detail_link remarks children_summary parent *'
    filter = models.Q(parent__isnull=True)
    variable_row_height = True


class SkillsByParent(Skills):
    label = _("Child skills")
    master_key = 'parent'
    column_names = 'seqno detail_link affinity *'
    order_by = ["seqno"]
    # order_by = ["parent", "seqno"]
    # order_by = ["name"]
    

class SkillsByType(Skills):
    master_key = 'skill_type' 

class Offers(dd.Table):
    model = 'skills.Competence'
    required_roles = dd.login_required(dd.SiteStaff)
    # required_roles = dd.login_required(SocialStaff)
    column_names = 'id user faculty description affinity *'
    order_by = ["id"]

    detail_layout = dd.DetailLayout("""
    user end_user
    faculty affinity
    description
    """, window_size=(60, 15))


class OffersByEndUser(Offers):
    required_roles = dd.login_required()
    master_key = 'end_user'
    column_names = 'faculty description affinity *'
    order_by = ["faculty"]
    

class OffersBySkill(Offers):
    master_key = 'faculty'
    column_names = 'user end_user affinity *'
    order_by = ["user"]


class MyOffers(My, Offers):
    required_roles = dd.login_required(SkillsStaff)
    label = _("Skills managed by me")
    column_names = 'faculty end_user description affinity *'
    order_by = ["faculty"]


class Demands(dd.Table):
    model = 'skills.Demand'
    required_roles = dd.login_required(dd.SiteStaff)
    # required_roles = dd.login_required(SocialStaff)
    column_names = 'id demander skill importance *'
    order_by = ["id"]
    stay_in_grid = True

    detail_layout = dd.DetailLayout("""
    demander
    skill 
    importance id
    """, window_size=(40, 'auto'))

class DemandsBySkill(Demands):
    label = _("Skill demands")
    required_roles = dd.login_required()
    master_key = 'skill'
    column_names = 'demander importance *'
    order_by = ["-importance", "-demander__id"]

class DemandsByDemander(Demands):
    label = _("Wanted skills")
    required_roles = dd.login_required()
    master_key = 'demander'
    # column_names = 'skill importance user *'
    column_names = 'skill importance *'
    order_by = ["-importance", "-skill__id"]

    # exclude_vote_states = 'author'

    detail_layout = dd.DetailLayout("""
    skill 
    importance
    """, window_size=(40, 'auto'))

    insert_layout = """
    skill
    importance
    """

    display_mode = 'summary'
    
    @classmethod
    def get_table_summary(self, obj, ar):
        """Customized :meth:`summary view
        <lino.core.actors.Actor.get_table_summary>` for this table.

        """
        sar = self.request_from(ar, master_instance=obj)

        html = []

        items = [
            ar.obj2html(o, str(o.skill)) for o in sar]

        sar = self.insert_action.request_from(sar)
        if sar.get_permission():
            btn = sar.ar2button()
            items.append(btn)
            
        if len(items) > 0:
            html += join_elems(items, sep=', ')
            
        return E.p(*html)
    

class OffersByDemander(Offers):
    required_roles = dd.login_required()
    master = dd.plugins.skills.demander_model
    column_names = '*'
    order_by = ["affinity"]
    display_mode = 'summary'
    

    @classmethod
    def get_request_queryset(self, ar):
        Offer = rt.models.skills.Competence
        Demand = rt.models.skills.Demand
        ticket = ar.master_instance
        if ticket is None:
            return Offer.objects.none()
        needed = set()
        for dem in Demand.objects.filter(demander=ticket):
            for sk in dem.skill.get_parental_line():
                needed.add(sk)
        return Offer.objects.filter(faculty__in=needed)

    @classmethod
    def get_table_summary(self, obj, ar):
        """Customized :meth:`summary view
        <lino.core.actors.Actor.get_table_summary>` for this table.

        """
        sar = self.request_from(ar, master_instance=obj)

        html = []

        items = [
            ar.obj2html(o, str(o.end_user)) for o in sar]

        if len(items) > 0:
            html += join_elems(items, sep=', ')
            
        return E.p(*html)
    


class AssignableWorkersByTicket(Users):
    # model = 'users.User'
    use_as_default_table = False
    # model = 'skills.Competence'
    master = dd.plugins.skills.demander_model  # 'tickets.Ticket'
    column_names = 'username #skills_competence_set_by_user__affinity *'
    label = _("Assignable workers")
    # required_roles = dd.login_required(Triager)

    @classmethod
    def get_request_queryset(self, ar):
        ticket = ar.master_instance
        if ticket is None:
            return rt.models.users.User.objects.none()

        # rt.models.skills.Competence.objects.filter(
        #     faculty=ticket.faculty)
        qs = rt.models.users.User.objects.all()
        # qs = super(
        #     AssignableWorkersByTicket, self).get_request_queryset(ar)

        topic = ticket.get_topic()
        if topic:
            qs = qs.filter(
                skills_competence_set_by_user__topic=topic)
        cond = models.Q()
        for dem in rt.models.skills.Demand.objects.filter(
                demander=ticket):
            skills = dem.skill.get_parental_line()
            cond |= models.Q(
                skills_competence_set_by_user__faculty__in=skills)
        qs = qs.filter(cond)
        qs = qs.order_by('skills_competence_set_by_user__affinity')
        return qs


if dd.is_installed('tickets'):

    from lino_xl.lib.tickets.roles import Triager, Reporter
    from lino_xl.lib.tickets.ui import Tickets


    class SuggestedTicketsByEndUser(Tickets):
        """Shows the tickets of other users which need help on a faculty for
        which I am competent.

        """
        master = dd.plugins.skills.end_user_model
        label = _("Where I can help")
        required_roles = dd.login_required(Reporter)
        column_names = 'detail_link:50 needed_skills ' \
                       'workflow_buttons:30 *'
        params_panel_hidden = True
        params_layout = """
        end_user feasable_by site #project state
        show_assigned show_active #topic"""

        @classmethod
        def param_defaults(self, ar, **kw):
            kw = super(SuggestedTicketsByEndUser, self).param_defaults(ar, **kw)
            mi = ar.master_instance
            if mi is None:
                mi = ar.get_user()
            # print("20170318 master instance is", mi)
            # kw.update(not_assigned_to=mi)
            kw.update(feasable_by=mi)
            # kw.update(show_assigned=dd.YesNo.no)
            kw.update(show_active=dd.YesNo.yes)
            return kw
