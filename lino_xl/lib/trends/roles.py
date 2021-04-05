# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""User roles for this plugin."""

from lino.core.roles import UserRole

   
class TrendsUser(UserRole):
    """A user who has access to trends functionality.

    """


class TrendsStaff(TrendsUser):
    """A user who can configure trends functionality.

    """

