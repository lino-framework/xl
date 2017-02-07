# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
Tables for this plugin.

"""

from __future__ import unicode_literals

from lino.api import dd, rt, _



class ShowEventsByDay(dd.Action):
    label = _("Today")
    help_text = _("Show all calendar events of the same day.")
    show_in_bbar = True
    sort_index = 60
    icon_name = 'calendar'

    def __init__(self, date_field, **kw):
        self.date_field = date_field
        super(ShowEventsByDay, self).__init__(**kw)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        today = getattr(obj, self.date_field)
        pv = dict(start_date=today)
        pv.update(end_date=today)
        sar = ar.spawn(rt.actors.cal.EventsByDay, param_values=pv)
        js = ar.renderer.request_handler(sar)
        ar.set_response(eval_js=js)


