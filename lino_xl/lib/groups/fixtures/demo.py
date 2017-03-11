# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


from lino.api import rt, _
from lino.utils.mldbc import babel_named as named


def objects():
    Group = rt.models.groups.Group
    User = rt.models.users.User
    UserTypes = rt.actors.users.UserTypes

    yield named(Group, _("Hitchhiker's Guide to the Galaxy"))
    yield named(Group, _("Star Trek"))
    yield named(Group, _("Harry Potter"))

    yield User(username="andy", profile=UserTypes.user)
    yield User(username="bert", profile=UserTypes.user)
    yield User(username="chloe", profile=UserTypes.user)
