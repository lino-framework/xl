# -*- coding: UTF-8 -*-
# Copyright 2013-2019 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Adds functionality for managing courses or other activities.

See :doc:`/specs/orders`.

"""

from django.utils.text import format_lazy

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Orders")
    worker_model = 'contacts.Person'
    worker_name_fields = "worker__name"
    needs_plugins = ['lino_xl.lib.cal']


    def on_site_startup(self, site):
        from lino.mixins import Contactable
        from lino_xl.lib.courses.mixins import Enrollable
        self.worker_model = site.models.resolve(self.worker_model)
        if not issubclass(self.worker_model, Enrollable):
            if False: # disabled because it causes sphinx-build to fail
                site.logger.warning(
                    "worker_model must be enrollable but %s isn't",
                    self.worker_model)

        # name = site.models.courses.Course._meta.verbose_name
        # # site.models.courses.CourseStates.verbose_name = format_lazy(_("{} state"), name)
        # site.models.courses.CourseStates.verbose_name_plural = format_lazy(_("{} states"), name)
        #
        # name = site.models.courses.Enrolment._meta.verbose_name
        # # site.models.courses.EnrolmentStates.verbose_name = format_lazy(_("{} state"), name)
        # site.models.courses.EnrolmentStates.verbose_name_plural = format_lazy(_("{} states"), name)

        super(Plugin, self).on_site_startup(site)
        
    def setup_main_menu(self, site, user_type, main):
        m = main.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.MyCourses')
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

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.Topics')
        m.add_action('courses.Slots')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.AllActivities')
        m.add_action('courses.AllEnrolments')
        m.add_action('courses.EnrolmentStates')
        m.add_action('courses.CourseAreas')
        m.add_action('courses.CourseStates')

    def get_dashboard_items(self, user):
        for x in super(Plugin, self).get_dashboard_items(user):
            yield x
        if user.authenticated:
            yield self.site.models.courses.MyCoursesGiven
            yield self.site.models.courses.MyCourses
        yield self.site.models.courses.StatusReport
