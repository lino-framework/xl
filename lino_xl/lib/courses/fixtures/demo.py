# -*- coding: UTF-8 -*-
# Copyright 2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

Create one activity line per activity layout.

"""
import datetime
from django.conf import settings

from lino.api import dd, rt, _

def objects():
    ActivityLayouts = rt.models.courses.ActivityLayouts
    EventType = rt.models.cal.EventType
    Line = rt.models.courses.Line

    # kw = dd.str2kw('name', _("Activities"))
    # kw.update(dd.str2kw('event_label', _("Hour")))
    # obj = EventType(**kw)
    # yield obj
    # settings.SITE.site_config.default_event_type = obj
    # yield settings.SITE.site_config

    for al in ActivityLayouts.get_list_items():
        yield Line(**dd.str2kw('name', al.text))
