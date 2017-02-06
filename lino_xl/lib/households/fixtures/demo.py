# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)
"""Adds demo data for `households`

Creates some households by marrying a few Persons.

Every third household gets divorced: we put an `end_date` to that
membership and create another membership for the same person with
another person.

"""

from django.conf import settings
from lino.core.utils import resolve_model


from lino.utils import Cycler
from lino.utils import i2d
from lino.api import dd, rt


def objects():

    Member = rt.modules.households.Member
    MemberRoles = rt.modules.households.MemberRoles
    # Household = resolve_model('households.Household')
    Person = dd.plugins.households.person_model
    Type = resolve_model('households.Type')

    men = Person.objects.filter(gender=dd.Genders.male).order_by('-id')
    women = Person.objects.filter(gender=dd.Genders.female).order_by('-id')
    if dd.is_installed('humanlinks'):
        # avoid interference with persons created by humanlinks demo
        # because these have already their households:
        men = men.filter(household_members__isnull=True)
        men = men.filter(humanlinks_children__isnull=True)
        men = men.filter(humanlinks_parents__isnull=True)
        women = women.filter(humanlinks_children__isnull=True)
        women = women.filter(humanlinks_parents__isnull=True)
        women = women.filter(household_members__isnull=True)
    
    MEN = Cycler(men)
    WOMEN = Cycler(women)
    TYPES = Cycler(Type.objects.all())

    if not len(MEN) or not len(WOMEN):
        raise Exception(
            "Not enough persons in {} and {} (all: {})".format(
                men, women, Person.objects.all()))

    # avoid automatic creation of children
    # loading_from_dump = settings.SITE.loading_from_dump
    # settings.SITE.loading_from_dump = True
    ses = rt.login()
    for i in range(5):
        pv = dict(
            head=MEN.pop(), partner=WOMEN.pop(),
            type=TYPES.pop())
        ses.run(
            Person.create_household,
            action_param_values=pv)
        # yield ses.response['data_record']
        # he = MEN.pop()
        # she = WOMEN.pop()
        
        # fam = Household(name=he.last_name + "-" + she.last_name, type_id=3)
        # yield fam
        # yield Member(household=fam, person=he, role=Role.objects.get(pk=1))
        # yield Member(household=fam, person=she, role=Role.objects.get(pk=2))

    i = 0
    for m in Member.objects.filter(role=MemberRoles.head):
        i += 1
        if i % 3 == 0:
            m.end_date = i2d(20020304)
            yield m

            pv = dict(
                head=m.person, partner=WOMEN.pop(),
                type=TYPES.pop())
            ses.run(
                Person.create_household,
                action_param_values=pv)
            
    # settings.SITE.loading_from_dump = loading_from_dump
