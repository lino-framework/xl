# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""
Roles for this plugin.

"""
from lino.core.roles import UserRole

class ExcerptsUser(UserRole):
    """Can print documents using database excerpts."""

class ExcerptsStaff(ExcerptsUser):
    """Can configure database excerpts functionality."""
