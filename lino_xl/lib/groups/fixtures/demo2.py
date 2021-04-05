# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)


from lino.api import rt, _
from lino.utils import Cycler
from lino.utils.instantiator import create_row
from lino.utils.mldbc import babel_named as named


def objects():
    Group = rt.models.groups.Group
    User = rt.models.users.User
    Membership = rt.models.groups.Membership
    Comment = rt.models.comments.Comment

    USERS = Cycler(User.objects.all())

    for grp in Group.objects.all():
        for i in range(2):
            u = USERS.pop()
            mbr = create_row(Membership, group=grp, user=u)
            yield mbr
            txt = _("Hi all, my name is {} and I am new here.").format(
                u)
            yield Comment(owner=grp, user=u, body=txt)
