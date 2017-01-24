# Copyright 2015-2016 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.contacts`. """

from lino.core.roles import SiteUser


class CoachingsUser(SiteUser):
    """A user who has access to basic coachings functionality.

    """
    
class CoachingsStaff(CoachingsUser):
    """A user who can configure coaching functionality.

    """

