# Copyright 2015-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

from lino.api import _
from lino.core.roles import UserRole


class CareerUser(UserRole):
    """Has access to career functionality"""


class CareerStaff(CareerUser):
    """Can configure career functionality."""


