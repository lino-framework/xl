# -*- coding: UTF-8 -*-
# Copyright 2009-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

u"""
Projects
--------

Adds tables Project and ProjectType

"""

from django.db import models

from lino.api import dd, _
from lino import mixins
from lino.modlib.users.mixins import My, UserAuthored
from lino.modlib.printing.mixins import CachedPrintable


class ProjectType(mixins.BabelNamed):

    class Meta:
        app_label = 'projects'
        verbose_name = _("Project Type")
        verbose_name_plural = _("Project Types")


class ProjectTypes(dd.Table):
    model = ProjectType
    order_by = ["name"]

#
# PROJECT
#

@dd.python_2_unicode_compatible
class Project(UserAuthored, CachedPrintable):

    class Meta:
        app_label = 'projects'
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    name = models.CharField(max_length=200)
    type = models.ForeignKey(ProjectType, blank=True, null=True)
    started = models.DateField(blank=True, null=True)
    stopped = models.DateField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

#~ class ProjectDetail(layouts.FormLayout):
    #~ datalink = 'projects.Project'
    #~ main = """
    #~ name type
    #~ started stopped
    #~ text
    #~ """


class Projects(dd.Table):
    model = 'projects.Project'
    order_by = ["name"]
    #~ button_label = _("Projects")
    detail_layout = """
    name type user
    started stopped
    text
    """


class MyProjects(My, Projects):
    pass


