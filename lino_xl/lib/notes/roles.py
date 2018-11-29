# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.core.roles import UserRole


class NotesUser(UserRole):
    pass


class NotesStaff(NotesUser):
    pass

