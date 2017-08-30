# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.polls`.

"""

from lino.core.roles import UserRole, SiteUser, SiteAdmin


class PollsUser(UserRole):
    pass


class PollsStaff(PollsUser):
    pass


class PollsAdmin(PollsStaff, SiteAdmin):
    pass


