# Copyright 2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.roles import UserRole


class NotesUser(UserRole):
    pass


class NotesStaff(NotesUser):
    pass

