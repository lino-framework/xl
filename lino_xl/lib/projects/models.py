# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

u"""
Projects
--------

Adds tables Project and ProjectType

"""

from django.db import models

from lino.api import dd, _
from lino import mixins
from lino.modlib.users.mixins import ByUser, UserAuthored
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


class MyProjects(Projects, ByUser):
    pass


