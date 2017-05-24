# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre

"""
Actions for `lino_xl.lib.github`.

"""

from lino.api import dd, rt, _
import logging
logger = logging.getLogger(__name__)

class import_all_commits(dd.Action):
    """
    Goes though all commits and check if they exist the the DB,
    also tries to find tickets that associate with the commit
    """
    show_in_bbar = True
    icon_name = 'import'
    # sort_index = 52
    label = _("Import All")

    def run_from_ui(self, ar, **kw):
        repo = ar.selected_rows[0]
        Commit = rt.models.github.Commit
        Session = rt.models.clocking.Session
        Ticket = rt.models.tickets.Ticket
        User = rt.models.users.User
        users = {}
        unknown_users = []
        for c in repo.github_api_get_all_comments():
            commit = Commit.from_api(c)

            #Find the user for this commit
            commit.user = users.get(commit.git_user,None)
            #not a huge fan of this, just want to avoide having to call filter for every commit
            if commit.user is None and commit.git_user not in unknown_users:
                user = User.objects.filter(github_username=commit.git_user)
                if len(user):
                    user = user[0]
                    commit.user = user
                    users[commit.git_user] = user
                else:
                    unknown_users.append(commit.git_user)

            #Parse the title if there's  a ticket #

            #if no ticket # find Sessions during that time
            if commit.user:
                sessions = Session.objects.filter(
                    #session start day <= commit day
                    #Session end day >= commit day
                    #Session start time <= commit time
                    #Session end time >= commit time
                    #   also need to check for timezones
                    #   commit time is UTC
                    #   unsure what timezone the session time is in.
                    )

