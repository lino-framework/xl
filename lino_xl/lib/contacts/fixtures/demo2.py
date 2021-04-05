# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt

from lino_xl.lib.contacts.management.commands.garble_persons import EstonianDistribution
from lino.utils import join_words


def build_dist(k):
    k = k.upper()
    # if k == 'BE':
    #     return BelgianDistribution()
    if k == 'EE':
        return EstonianDistribution()


def objects():

    dist = build_dist(dd.plugins.countries.country_code)

    if dist is None:
        return

    User = rt.models.users.User
    Person = rt.models.contacts.Person

    for p in Person.objects.order_by('id'):
        if User.objects.filter(partner=p).count() > 0:
            # users keep their original name
            pass
        else:
            p.last_name = dist.LAST_NAMES.pop()
            if p.gender == dd.Genders.male:
                p.first_name = dist.MALES.pop()
                dist.FEMALES.pop()
            else:
                p.first_name = dist.FEMALES.pop()
                dist.MALES.pop()
            p.name = join_words(p.last_name, p.first_name)
            dist.before_save(p)
            yield p
