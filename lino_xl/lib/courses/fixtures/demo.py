# -*- coding: UTF-8 -*-
# Copyright 2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""

Create one activity line per activity layout.

"""
import datetime
from django.conf import settings

from lino.api import dd, rt, _

def objects():
    CourseAreas = rt.models.courses.CourseAreas
    Line = rt.models.courses.Line
    for al in CourseAreas.get_list_items():
        yield Line(**dd.str2kw('name', al.text))
