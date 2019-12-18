# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _
from lino.utils.mldbc import babeld
from lino.utils import Cycler


def objects():
    List = rt.models.lists.List
    Member = rt.models.lists.Member
    Partner = rt.models.contacts.Partner

    LISTS = Cycler(List.objects.order_by('id'))

    for p in dd.plugins.lists.partner_model.objects.order_by('id'):
        yield Member(partner=p, list=LISTS.pop())
