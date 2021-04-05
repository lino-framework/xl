# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
This defines the :class:`Feasible` model mixin.

"""

from lino.api import dd, rt, _
from etgen.html import E
from lino.utils import join_elems

class Feasible(dd.Model):
    """Any model which inherits from this mixin becomes "feasible".
    """
    class Meta:
        abstract = True

    #To allow tickets to inherit from this mixin
    #in the base class without skills installed
    if dd.is_installed('skills'):

        def get_topic(self):
            return None

        @dd.displayfield(_("Suppliers"))
        def suppliers(self, ar):
            """Displays a list of candidate suppliers.

            This means: all suppliers who have at least one of the
            skills required by this object.

            """
            if ar is None:
                return ''

            if not isinstance(self, dd.plugins.skills.demander_model):
                return ''
            
            Offer = rt.models.skills.Competence
            Demand = rt.models.skills.Demand
            skills = set()
            for dem in Demand.objects.filter(demander=self):
                skills.add(dem.skill)
                # skills |= set(dem.skill.get_parental_line())

            elems = []
            for spl in Offer.objects.filter(faculty__in=skills):
                if spl.end_user is not None:
                    elems.append(spl.end_user.obj2href(ar))
            elems = join_elems(elems, ', ')
            return E.p(*elems)

        @dd.displayfield(_("Needed skills"))
        def needed_skills(self, ar):
            """Displays a list of needed skills.

            This means: all skill demands for this object.

            """
            if ar is None:
                return ''
            if not isinstance(self, dd.plugins.skills.demander_model):
                return ''
            Demand = rt.models.skills.Demand
            elems = []
            for dem in Demand.objects.filter(demander=self):
                elems.append(dem.skill.obj2href(ar))
            elems = join_elems(elems, ', ')
            return E.span(*elems)

        @classmethod
        def setup_parameters(cls, fields):
            super(Feasible,cls).setup_parameters(fields)
            fields.update(
                feasable_by = dd.ForeignKey(
                    # settings.SITE.user_model,
                    dd.plugins.skills.end_user_model,
                    verbose_name=_("Feasable by"),
                    blank=True, null=True))

        @classmethod
        def get_request_queryset(cls, ar):
            qs = super(Feasible, cls).get_request_queryset(ar)
            pv = ar.param_values

            if pv.feasable_by:
                # show only tickets which have at least one demand that
                # matches a skill supply authored by the specified user.
                skills = set()
                for fac in rt.models.skills.Skill.objects.filter(
                        competence__end_user=pv.feasable_by):
                    skills |= set(fac.get_parental_line())
                # if True:  # TODO: test whether supplier_model inherits from User
                #     for fac in rt.models.skills.Skill.objects.filter(
                #             competence__user=pv.feasable_by):
                #         skills |= set(fac.get_parental_line())
                qs = qs.filter(demand__skill__in=skills)
                qs = qs.distinct()
            return qs
