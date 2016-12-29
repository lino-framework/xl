# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
#
# License: BSD (see file COPYING for details)
"""
Roles for this plugin.

"""
from lino.core.roles import SiteUser

class ExcerptsUser(SiteUser):
    pass

class ExcerptsStaff(ExcerptsUser):
    pass
