# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""User roles for this plugin.

"""

from lino.core.roles import UserRole


class SkillsUser(UserRole):
    pass

class SkillsStaff(SkillsUser):
    pass
