# -*- coding: UTF-8 -*-# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""User interface for this plugin.

"""

from lino.api import dd, rt, _

from lino import mixins
from lino.utils.xmlgen.html import E
from django.contrib.humanize.templatetags.humanize import naturaltime

from lino.core.roles import Explorer
from lino_xl.lib.tickets.roles import TicketsStaff, TicketsUser
from lino.modlib.users.mixins import My
from lino.mixins.periods import ObservedPeriod

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
    required_roles = dd.login_required((TicketsUser,))
    model = 'github.Commit'
    column_names = 'repository sha ticket user git_user summary created comment:10 *'
    detail_layout = """
        repository sha ticket
        user git_user url
        summary comment
        description
    """
    order_by = ["-created"]

    parameters = ObservedPeriod()
    #todo add params for repo, not assigned

class CommitsByRepository(Commits):
    master_key = 'repository'
    column_names = 'sha ticket summary user git_user created comment:10 *'


class CommitsByTicket(Commits):
    master_key = 'ticket'
    column_names = 'repository summary user url'
    slave_grid_format = "summary"
    # stay_in_grid = True

    @classmethod
    def get_slave_summary(self, obj, ar):
        sar = self.request_from(ar, master_instance=obj)
        html = ""
        html += "<ul>"
        for c in sar:
            #todo have another js button that will expend the summary into the complete description.
            html += "<li><a href={commit_url}>{sha}</a>:{user}:{date}<br/>{summary}</li>".format(
                commit_url = c.url,
                sha = c.sha[:6],
                user = E.tostring(ar.obj2html(c.user, str(c.user))),
                date = E.tostring(ar.obj2html(c, naturaltime(c.created),title = c.created.strftime('%Y-%m-%d %H:%M'))),
                summary=c.summary,
            )

        html += "</ul>"

        return ar.html_text(html)

class CommitsByUser(Commits):
    master_key = 'user'
    column_names = 'repository summary ticket url'

class MyCommits(My, Commits):
    column_names = 'repository summary ticket url'