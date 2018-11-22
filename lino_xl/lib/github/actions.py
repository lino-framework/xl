# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd

"""
Actions for `lino_xl.lib.github`.

"""

from lino.api import dd, rt, _
import logging
logger = logging.getLogger(__name__)
from django.db.models import Q

class User_commit_finder():

    def __init__(self):
        self.users = {}
        self.unknown_users = []

    def find_user(self, commit):
        """
        tryes to match a User to a commit,
        Either returns a User instance or None
        :param commit:
        :return:
        """
        # Find the user for this commit
        User = rt.models.users.User
        found_user = self.users.get(commit.git_user, None) or self.users.get(commit.commiter_name, None)
        # not a huge fan of this, just want to avoid having to call filter for every commit
        if found_user is None and \
                (commit.git_user not in self.unknown_users or commit.commiter_name not in self.unknown_users):
            found_user = User.objects.filter(
                Q(github_username=commit.git_user) | Q(first_name__contains=commit.commiter_name.split()[0]))
            if len(found_user):
                found_user = found_user[0]
                if commit.git_user:
                    self.users[commit.git_user] = found_user
                else:
                    self.users[commit.commiter_name] = found_user
            else:
                found_user = None
                if commit.git_user:
                    self.unknown_users.append(commit.git_user)
                if commit.commiter_name:
                    self.unknown_users.append(commit.commiter_name)
                # self.unknown_users.append(commit.git_user or commit.commiter_name)
        return found_user


class Import_all_commits(dd.Action):
    """
    Goes though all commits and check if they exist the the DB,
    also tries to find tickets that associate with the commit
    """
    show_in_bbar = True
    button_text = 'import'
    # sort_index = 52
    label = _("Import All")

    def get_commits(self, **kw):
        for c in kw.get('repo').github_api_get_all_comments(sha=kw.get('sha', None)):
            #todo Check to make sure the request worked or not
            commit = rt.models.github.Commit.from_api(c, kw.get('repo'))
            yield commit


    def run_from_ui(self, ar, **kw):
        repo = ar.selected_rows[0]
        kw['repo'] = repo
        self.run_from_code(ar, **kw)
        ar.set_response(refresh_all=True)

    def run_from_code(self, ar, *args, **kw):
        repo = kw.get('repo', None)
        if repo is None:
            repo = ar.selected_rows[0]
            kw['repo'] = repo
        Ticket = rt.models.tickets.Ticket
        user_finder = User_commit_finder()
        for commit in self.get_commits(**kw):
            commit.user = user_finder.find_user(commit)

            # Parse the title if there's  a ticket #
            ticket_ids = dd.plugins['github'].ticket_pattern.findall(commit.description)
            if ticket_ids:
                try:
                    commit.ticket = Ticket.objects.get(**{Ticket._meta.pk.name: ticket_ids[0]})
                except Ticket.DoesNotExist:
                    pass

            # if no ticket # find Sessions during that time and pick ticket
            if commit.ticket is None and commit.user is not None:
                sessions = self.find_sessions(commit, commit.user)
                if len(sessions) == 1:
                    commit.ticket = sessions[0].ticket
                elif len(sessions) > 1:
                    commit.ticket = sessions[0].ticket
                    commit.comment = ", ".join([str(s.ticket) for s in sessions])
            # commit.full_clean() #Just update records
            commit.save()

    @staticmethod
    def find_sessions(commit, user):
        return rt.models.working.Session.objects.filter(
            Q(user=user),
            (Q(start_date=commit.created.date()) & Q(end_date__isnull=True)) | #Because some sessiosn don't have a end_date but are finished on the same day.
            (Q(start_date__lte=commit.created.date()) & Q(end_date__gte=commit.created.date())),
            Q(start_time__lte=commit.created.time()),
            Q(end_time__gte=commit.created.time()) | Q(end_date=None))

class Import_new_commits(Import_all_commits):
    """
    Collects commit lists, only import commits untill a known SHA is found.
    """

    show_in_bbar = True
    button_text = 'Update'
    # sort_index = 52
    label = _("Import New")


    def get_commits(self, **kw):
        shas = frozenset(
            sha[0] for sha in rt.models.github.Commit.objects.values_list('sha')
                        )
        for commit in super(Import_new_commits, self).get_commits(**kw):
            if commit.sha in shas:
                break
            else:
                yield commit


class Update_all_repos(Import_new_commits):
    show_in_bbar = True
    button_text = 'Update All'
    # sort_index = 52
    label = _("Import New from All Repos")

    def run_from_ui(self, ar, **kw):
        # repo = ar.selected_rows[0] #
        self.run_from_code(ar, **kw)
        ar.set_response(refresh_all=True)

    def run_from_code(self, ar, *args, **kw):
        for repo in rt.models.github.Repository.objects.all():
            kw['repo'] = repo
            # try:
            super(Update_all_repos, self).run_from_code(ar, *args, **kw)
            # except Exception as e:
            #     logger.exception("e")
