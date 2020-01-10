# Copyright 2013-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Adds a calendar view. See :doc:`/specs/calview`.

"""

from lino.api import ad, _
from dateutil.relativedelta import relativedelta


class Plugin(ad.Plugin):
    verbose_name = _("Calendar view")

    needs_plugins = ['lino_xl.lib.cal']

    def setup_main_menu(self, site, user_type, m):
        mg = site.plugins.cal
        m = m.add_menu(mg.app_label, mg.verbose_name)
        a = site.models.calview.MonthlyView
        m.add_instance_action(a.get_row_by_pk(None, "0"), action=a.default_action, label=_("Calendar view"))

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.cal
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('calview.DailyPlannerRows')

    def get_dashboard_items(self, user):
        if user.authenticated:
            yield self.site.models.calview.DailyPlanner
