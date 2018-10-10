# Copyright 2015-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.contacts`. """

from lino.core.roles import UserRole


class CoachingsUser(UserRole):
    """Can coach clients."""

    
class CoachingsStaff(CoachingsUser):
    """Can configure coaching functionality."""
