# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)


from lino.core.roles import UserRole


class SepaUser(UserRole):
    """Can see imported statements and movements per partner."""
    pass


class SepaStaff(SepaUser):
    """Can see imported statements and movements also globally in the
    :menuselection`Explorer` menu.

    """
    pass


