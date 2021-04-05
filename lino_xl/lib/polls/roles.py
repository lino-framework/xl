# Copyright 2015-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""User roles for `lino_xl.lib.polls`.

"""

from lino.core.roles import UserRole, SiteUser, SiteAdmin


class PollsUser(UserRole):
    "Can see polls and create new responses."
    pass


class PollsStaff(PollsUser):
    "Can create new polls."
    pass


class PollsAdmin(PollsStaff, SiteAdmin):
    "Can configure polls functionality."
    pass


