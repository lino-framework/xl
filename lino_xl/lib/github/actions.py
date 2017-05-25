# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre

"""
Actions for `lino_xl.lib.github`.

"""

from lino.api import dd, rt, _
import logging
logger = logging.getLogger(__name__)
from django.db.models import Q

class Import_all_commits(dd.Action):
    """
    Goes though all commits and check if they exist the the DB,
    also tries to find tickets that associate with the commit
    """
    show_in_bbar = True
    button_text = 'import'
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
            commit = Commit.from_api(c, repo)

            #Find the user for this commit
            commit.user = users.get(commit.git_user,None)
            #not a huge fan of this, just want to avoide having to call filter for every commit
            if commit.user is None and commit.git_user not in unknown_users and commit.git_user:
                user = User.objects.filter(Q(github_username=commit.git_user)|Q(first_name__contains=commit.git_user.split()[0]))
                if len(user):
                    user = user[0]
                    commit.user = user
                    users[commit.git_user] = user
                else:
                    unknown_users.append(commit.git_user)

            #Parse the title if there's  a ticket #
            ticket_ids = dd.plugins['github'].ticket_pattern.findall(commit.description)
            if ticket_ids:
                try:
                    commit.ticket = Ticket.objects.get(**{Ticket._meta.pk.name : ticket_ids[0]})
                except Ticket.DoesNotExist:
                    pass

            #if no ticket # find Sessions during that time and pick ticket
            if commit.ticket is None and commit.user is not None:
                sessions = Session.objects.filter(
                    user=commit.user,
                    start_date__lte=commit.created.date(),
                    end_date__gte=commit.created.date(),
                    start_time__lte=commit.created.time(),
                    end_time__gte=commit.created.time()
                                        )
                if len(sessions) == 1:
                    commit.ticket = sessions[0].ticket
                elif len(sessions) > 1:
                    commit.ticket = sessions[0].ticket
                    commit.comment = ", ".join([s.ticket for s in sessions])
            # commit.full_clean() #Just update records
            commit.save()
        ar.set_response(refresh_all=True)