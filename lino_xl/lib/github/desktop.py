# -*- coding: UTF-8 -*-# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""User interface for this plugin.

"""

from lino.api import dd, rt, _

from lino import mixins
from etgen.html import E
from django.contrib.humanize.templatetags.humanize import naturaltime

from lino.core.roles import Explorer
from lino_xl.lib.tickets.roles import TicketsStaff, Triager, Reporter
from lino.modlib.users.mixins import My
from lino.mixins.periods import ObservedDateRange

from .models import Commit, Repository

"""
    All Repos
    All commits
    My commits
    My Unasigned Commits
    commits By ticket
    commits by user
    commits by unknown user
"""

class Repositories(dd.Table):
    """ Base table for Repositories
    """
    required_roles = dd.login_required((TicketsStaff,))
    model = 'github.Repository'
    detail_layout = """
        user_name repo_name o_auth size
        CommitsByRepository
    """
    insert_layout = dd.InsertLayout("""
        user_name
        repo_name
        o_auth
    """)
    column_names = 'user_name repo_name size'
    hidden_columns = "o_auth"

class Commits(dd.Table):
    """Base table for Commits"""
    required_roles = dd.login_required((Triager, Reporter))
    model = 'github.Commit'
    column_names = 'repository sha ticket user git_user summary created comment:10 *'
    detail_layout = """
        repository sha ticket
        user git_user url
        created comment
        description
    """
    order_by = ["-created"]

    parameters = ObservedDateRange()
    #todo add params for repo, not assigned

class CommitsByRepository(Commits):
    master_key = 'repository'
    column_names = 'sha ticket summary user git_user created comment:10 *'


class CommitsByTicket(Commits):
    master_key = 'ticket'
    column_names = 'repository summary user url'
    display_mode = "summary"
    # stay_in_grid = True

    @classmethod
    def get_table_summary(self, obj, ar):
        sar = self.request_from(ar, master_instance=obj)
        items = []
        for c in sar:
            # todo have another js button that will expand the summary
            # into the complete description.
            items.append(E.li(
                E.a(c.sha[:6], href=c.url, target="_BLANK"),
                ":" if c.user else "",
                ar.obj2html(c.user) if c.user else "",
                ":",
                ar.obj2html(
                    c, naturaltime(c.created),
                    title=c.created.strftime('%Y-%m-%d %H:%M')),
                E.br(), c.summary))
        return E.ul(*items)

class CommitsByUser(Commits):
    master_key = 'user'
    column_names = 'repository summary ticket url'

class MyCommits(My, Commits):
    column_names = 'repository summary ticket url'
