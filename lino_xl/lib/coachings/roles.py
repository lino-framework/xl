# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.contacts`. """

from lino.core.roles import UserRole


class CoachingsUser(UserRole):
    pass
    
class CoachingsStaff(CoachingsUser):
    pass
