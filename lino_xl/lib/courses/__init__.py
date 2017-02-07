# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Adds functionality for managing activities.

An **activity** is a series of scheduled calendar events where a given
teacher teaches a given group of participants about a given topic.

There is a configurable list of **topics**.  Activities are grouped
into **activity lines** (meaning "series").  An activity line is a
series of activities having a same **topic**.

The participants of an activity are stored as **Enrolments**.

The internal name "courses" of this plugin and the main model is for
historic reasons.  


.. autosummary::
   :toctree:

   models
   choicelists
   workflows
   desktop

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Activities")
    teacher_model = 'contacts.Person'
    pupil_model = 'contacts.Person'
    pupil_name_fields = "pupil__name"

    needs_plugins = ['lino_xl.lib.cal']

    def on_site_startup(self, site):
        from lino.core.fields import fields_list
        self.pupil_model = site.models.resolve(self.pupil_model)
        self.teacher_model = site.models.resolve(self.teacher_model)
        # self.pupil_name_fields = set(self.pupil_name_fields.split())
        self.pupil_name_fields = fields_list(
            site.models.courses.Enrolment, self.pupil_name_fields)
        super(Plugin, self).on_site_startup(site)
        
    def day_and_month(self, d):
        if d is None:
            return "-"
        return d.strftime("%d.%m.")

    def setup_main_menu(self, site, profile, main):
        m = main.add_menu(self.app_label, self.verbose_name)
        for ca in site.models.courses.CourseAreas.objects():
            m.add_action(ca.courses_table)
        # m.add_action('courses.BasicCourses')
        # m.add_action('courses.JobCourses')
        # m.add_action('courses.DraftCourses')
        # m.add_action('courses.ActiveCourses')
        # m.add_action('courses.InactiveCourses')
        # m.add_action('courses.ClosedCourses')
        m.add_separator()
        m.add_action('courses.Lines')
        m.add_action('courses.PendingRequestedEnrolments')
        m.add_action('courses.PendingConfirmedEnrolments')
        m.add_action('courses.MyCoursesGiven')

    def setup_config_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.Topics')
        m.add_action('courses.Slots')

    def setup_explorer_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.AllActivities')
        m.add_action('courses.AllEnrolments')
        m.add_action('courses.EnrolmentStates')
        # m.add_action('courses.CourseAreas')

    def get_dashboard_items(self, user):
        for x in super(Plugin, self).get_dashboard_items(user):
            yield x
        yield self.site.actors.courses.MyCoursesGiven
