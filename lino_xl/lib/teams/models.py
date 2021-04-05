# Copyright 2016 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Database models for this plugin.

"""

from __future__ import unicode_literals

# import logging
# logger = logging.getLogger(__name__)


from lino.api import dd, _
from lino.mixins import BabelNamed, Referrable

# users = dd.resolve_app('users')


class Team(BabelNamed, Referrable):

    class Meta:
        app_label = 'teams'
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")
        abstract = dd.is_abstract_model(__name__, 'Team')


class Teams(dd.Table):
    model = 'teams.Team'
    required_roles = dd.login_required(dd.SiteStaff)
    column_names = 'ref name *'
    order_by = ["ref", "name"]

    insert_layout = """
    ref
    name
    """

    detail_layout = """
    id ref name 
    teams.UsersByTeam
    """


dd.inject_field(
    'users.User', 'team',
    dd.ForeignKey('teams.Team', blank=True, null=True))


from lino.modlib.users.desktop import Users

class UsersByTeam(Users):
    master_key = 'team'
