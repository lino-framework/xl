# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.polls`.

"""

from lino.core.roles import SiteUser, SiteAdmin


class PollsUser(SiteUser):
    """A user who has access to polls functionality.

    """


class PollsStaff(PollsUser):
    """A user who manages configuration of polls functionality.

    """


class PollsAdmin(PollsStaff, SiteAdmin):
    pass


