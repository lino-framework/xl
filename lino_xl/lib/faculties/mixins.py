# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
This defines the :class:`Feasible` model mixin.

"""

from lino.api import dd, rt, _
from lino.utils.xmlgen.html import E
from lino.utils import join_elems

class Feasible(dd.Model):
    """Any model which inherits from this mixin becomes "feasible".
    """
    class Meta:
        abstract = True

    #To allow tickets to inherit from this mixin
    #in the base class without faculties installed
    if dd.is_installed('faculties'):

        @dd.displayfield(_("Suppliers"))
        def suppliers(self, ar):
            """Displays a list of candidate suppliers.

            This means: all suppliers who have at least one of the
            skills required by this object.

            """
            if ar is None:
                return ''

            Offer = rt.models.faculties.Competence
            Demand = rt.models.faculties.Demand
            faculties = set()
            for dem in Demand.objects.filter(demander=self):
                faculties.add(dem.skill)
                # faculties |= set(dem.skill.get_parental_line())

            elems = []
            for spl in Offer.objects.filter(faculty__in=faculties):
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

            Demand = rt.models.faculties.Demand
            elems = []
            for dem in Demand.objects.filter(demander=self):
                elems.append(dem.skill.obj2href(ar))
            elems = join_elems(elems, ', ')
            return E.p(*elems)

        @classmethod
        def get_parameter_fields(cls, **fields):
            fields = super(Feasible,cls).get_parameter_fields(**fields)
            fields.update(
            feasable_by = dd.ForeignKey(
                # settings.SITE.user_model,
                dd.plugins.faculties.end_user_model,
                verbose_name=_("Feasable by"), blank=True, null=True),
            )
            return fields

        @classmethod
        def get_request_queryset(cls, ar):
            qs = super(Feasible, cls).get_request_queryset(ar)
            pv = ar.param_values

            if pv.feasable_by:
                # show only tickets which have at least one demand that
                # matches a skill supply authored by the specified user.
                faculties = set()
                for fac in rt.models.faculties.Faculty.objects.filter(
                        competence__end_user=pv.feasable_by):
                    faculties |= set(fac.get_parental_line())
                # if True:  # TODO: test whether supplier_model inherits from User
                #     for fac in rt.models.faculties.Faculty.objects.filter(
                #             competence__user=pv.feasable_by):
                #         faculties |= set(fac.get_parental_line())
                qs = qs.filter(demand__skill__in=faculties)
                qs = qs.distinct()
            return qs
