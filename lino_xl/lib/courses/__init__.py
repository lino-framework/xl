# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Adds functionality for managing activities.

An **activity** is a series of scheduled calendar events where a given
teacher teaches a given group of participants about a given topic.

The internal name "courses" of this plugin and its main model is for
historic reasons. In :ref:`welfare` they are called "workshops", in
:ref:`tera` they are called "therapies".

There is a configurable list of **topics**.  Activities are grouped
into **activity lines** (meaning "series").  An activity line is a
series of activities having a same **topic**.

The participants of an activity are stored as **Enrolments**.

.. autosummary::
   :toctree:

   models
   mixins
   choicelists
   workflows
   desktop


.. xfile:: presence_sheet.weasy.html

    The template used for printing a presence sheet of an activity
    (both versions pdf and html)

"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Activities")
    teacher_model = 'contacts.Person'
    pupil_model = 'contacts.Person'
    
    pupil_name_fields = "pupil__name"
    """The value to use as :attr:`quick_search_fields
    <lino.core.model.Model.quick_search_fields>` for
    :class:`Enrolment`. 

    Note that this remains a text string while
    :attr:`quick_search_fields
    <lino.core.model.Model.quick_search_fields>` is resolved into a
    set of field names at site startup.

    """

    needs_plugins = ['lino_xl.lib.cal']

    def unused_on_plugins_loaded(self, site):
        # from lino.core.fields import fields_list
        self.pupil_name_fields = set(self.pupil_name_fields.split())
        # self.pupil_name_fields = fields_list(
        #      site.models.courses.Enrolment, self.pupil_name_fields)
        super(Plugin, self).on_plugins_loaded(site)

    def on_site_startup(self, site):
        from lino.mixins import Contactable
        from lino_xl.lib.courses.mixins import Enrollable
        self.pupil_model = site.models.resolve(self.pupil_model)
        self.teacher_model = site.models.resolve(self.teacher_model)
        if not issubclass(self.teacher_model, Contactable):
            raise Exception("teacher_model must be contactable")
        if not issubclass(self.pupil_model, Enrollable):
            if False: # disabled because it causes sphinx-build to fail
                site.logger.warning(
                    "pupil_model must be enrollable but %s isn't", 
                    self.pupil_model)
        super(Plugin, self).on_site_startup(site)
        
    def setup_main_menu(self, site, user_type, main):
        m = main.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.MyActivities')
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
        # m.add_action('courses.CourseAreas')

    def get_dashboard_items(self, user):
        for x in super(Plugin, self).get_dashboard_items(user):
            yield x
        if user.authenticated:
            yield self.site.models.courses.MyCoursesGiven
            yield self.site.models.courses.MyActivities
        yield self.site.models.courses.StatusReport
