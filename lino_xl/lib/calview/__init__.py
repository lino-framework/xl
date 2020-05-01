# Copyright 2013-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Adds a calendar view. See :doc:`/specs/calview`.

"""

from lino.api import ad, _
from dateutil.relativedelta import relativedelta
from django.utils.text import format_lazy


class Plugin(ad.Plugin):
    "The descriptor for this plugin. See :class:`lino.core.Plugin`."
    verbose_name = _("Calendar view")

    needs_plugins = ['lino_xl.lib.cal']

    params_layout = """user assigned_to project event_type room state show_appointments"""
    """The actor parameter layout to use for filtering calendar views."""

    def setup_main_menu(self, site, user_type, m):
        mg = site.plugins.cal
        m = m.add_menu(mg.app_label, mg.verbose_name)
        for nav in site.models.calview.Planners.get_list_items():
            a = nav.default_view
            m.add_instance_action(a.get_row_by_pk(None, "0"), action=a.default_action,
                label=nav.text)

        # a = site.models.calview.MonthlyView
        # a = site.models.calview.WeeklyView
        # m.add_instance_action(a.get_row_by_pk(None, "0"), action=a.default_action,
        #     label=_("Calendar view"))
        #
        # from lino_xl.lib.calview.mixins import Plannable
        # from lino.core.utils import models_by_base
        # for pm in models_by_base(Plannable):
        #     a = pm.weekly_planner
        #     # a = site.models.calview.MonthlyView
        #     # a = site.models.calview.WeeklyView
        #     print(20200215, a)
        #     m.add_instance_action(a.get_row_by_pk(None, "0"), action=a.default_action,
        #         label=format_lazy(_("Calendar view {}"), pm._meta.verbose_name_plural))

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.cal
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('calview.DailyPlannerRows')

    def get_dashboard_items(self, user):
        # if user.authenticated:
        yield self.site.models.calview.DailyPlanner

    # def before_analyze(self):
    #     # dynamically create the calendar views
    #     from lino_xl.lib.calview.ui import make_calview_actors
    #     from lino_xl.lib.calview.mixins import Plannable
    #     from lino.core.utils import models_by_base
    #     for pm in models_by_base(Plannable):
    #         make_calview_actors(self.site, pm)
