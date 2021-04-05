# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import rt, _
from lino.utils.mldbc import babel_named as named


def objects():
    Group = rt.models.groups.Group
    User = rt.models.users.User
    UserTypes = rt.models.users.UserTypes

    yield named(Group, _("Hitchhiker's Guide to the Galaxy"))
    yield named(Group, _("Star Trek"))
    yield named(Group, _("Harry Potter"))

    yield User(username="andy", user_type=UserTypes.user, first_name="Andy")
    yield User(username="bert", user_type=UserTypes.user, first_name="Bert")
    yield User(username="chloe", user_type=UserTypes.user, first_name="Chloe")
