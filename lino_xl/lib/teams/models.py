# Copyright 2016 Luc Saffre
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

"""Database models for this plugin.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


from lino.api import dd
from lino import mixins
from django.utils.translation import ugettext_lazy as _

users = dd.resolve_app('users')


class Team(mixins.BabelNamed):

    class Meta:
        app_label = 'teams'
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        abstract = dd.is_abstract_model(__name__, 'Team')


class Teams(dd.Table):
    model = 'teams.Team'
    required_roles = dd.required(dd.SiteStaff)
    column_names = 'name *'
    order_by = ["name"]

    insert_layout = """
    name
    """

    detail_layout = """
    id name
    teams.UsersByTeam
    """


dd.inject_field(
    users.User, 'team',
    dd.ForeignKey('teams.Team', blank=True, null=True))


class UsersByTeam(users.Users):
    master_key = 'team'
