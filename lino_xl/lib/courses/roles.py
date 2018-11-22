# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.core.roles import UserRole


class CoursesTeacher(UserRole):
    "Can see and edit their own courses."
    pass

class CoursesUser(UserRole): # TODO: rename to CoursesCoordinator
    "Can see and edit all courses."
    pass

# class CoursesStaff(CoursesUser):
#     "Can edit all courses and configure the plugin."
#     pass
