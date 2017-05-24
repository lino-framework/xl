# -*- coding: UTF-8 -*-# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""User interface for this plugin.

"""

from lino.api import dd, rt, _

from lino import mixins

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
    column_names = 'repository sha ticket user git_user summary comment:10 *'
    detail_layout = """
        repository sha ticket
        user git_user url
        summary comment
        description
    """

    parameters = ObservedPeriod()

class CommitsByRepository(Commits):
    master_key = 'repository'
    column_names = 'sha ticket summary user git_user comment:10 *'


class CommitsByTicket(Commits):
    master_key = 'ticket'
    column_names = 'repository summary user url'

class CommitsByUser(Commits):
    master_key = 'user'
    column_names = 'repository summary ticket url'

class MyCommits(My, Commits):
    column_names = 'repository summary ticket url'