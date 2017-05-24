# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""Database models for this plugin.
"""

from lino.api import dd, rt, _
from django.db import models

from lino.mixins import Created
class Repository(dd.Model):
    """A **Repository** is a git username and repo name,
    along with an o-auth token to allow for more then 60 requests to
    github an hour

    .. attribute:: user_name

        Github username.

    .. attribute:: repo_name

        Name of Repo belonging to user_name

    .. attribute:: o_auth

        Access token to be used with github's api,
        https://github.com/settings/tokens/new
        For public repos create a token with no scope.
        For private repos the token must have repo commit access,
        because github doesn't provide a way for a token to have
        read only status, we recommend not using this module with
        private repos unless you are sure that the token is secure.

    """

    class Meta:
        app_label = 'github'
        verbose_name = _("Repository")
        verbose_name_plural = _('Repositories')
        abstract = dd.is_abstract_model(__name__, 'Repository')

    user_name = dd.CharField(_("User Name"),
                             max_length=39)
    repo_name = dd.CharField(_("Repository Name"),
                             max_length=100)
    o_auth    = dd.PasswordField(_("OAuth Token"),
                             max_length=40,
                             blank=True)

    def __str__(self):
        return "%s:%s"%(self.user_name, self.repo_name)

    @dd.displayfield(_("Url"))
    def url(self, ar):
        return "https://api.github.com/repos/%s/%s/"%(self.user_name,
                                                      self.repo_name)

    @dd.displayfield(_("Number Of commits"))
    def size(self, ar):
        return self.commits.count()

class Commit(Created):
    """A **Commit** is a git commit sha and other relevant data.

    .. attribute:: url

        Url pointing to the details for this commit on Github.

    .. attribute:: git_user

        The Github user who commited this commit.
        If there is a user who was linked to this commit via
        user.User.github_username this will be blank.

        Otherwise it will contain the username of the unknown commiter

    .. attribute:: user

        User who commited this commit to github, uses user.User.github_username

    .. attribute:: sha

        Primary Key
        40 Character sha1 hash for the commit

    .. attribute:: summary

        The summary of the commit.
    """

    class Meta:
        app_label = 'github'
        verbose_name = _("Commit")
        verbose_name_plural = _('Commits')
        abstract = dd.is_abstract_model(__name__, 'Commit')

    repository = dd.ForeignKey(Repository,
                               verbose_name=_("Repository"),
                               related_name="commits")

    user = dd.ForeignKey(
        'users.User',
        verbose_name=_("Author"),
        related_name="%(app_label)s_%(class)s_set_by_user",
        blank=True, null=True)
    ticket = dd.ForeignKey(
        'tickets.Ticket',
        verbose_name=_("Ticket"),
        related_name="Commits",
        blank=True, null=True)

    git_user = dd.CharField(_("Git User Name"),
                            blank=True,
                            max_length=39,)
    sha = dd.CharField(_("Sha Hash"),
                       max_length=40,
                       primary_key=True,
                       editable=False)
    url = dd.CharField(_("Commit page"),
                       max_length=255,
                       editable=False)
    description = dd.RichTextField(_("Description"),
                               editable=False,
                               blank=True, null=True)
    summary = dd.CharField(_("Summary"),
                               editable=False,
                               blank=True, null=True,
                           max_length=72)
    comment = dd.CharField(_("Comment"),
                           max_length=50)

    unassignable = models.BooleanField(_("Unassignable"),
                                       default=False,
                                       editable=True)

dd.inject_field(
    "users.User", 'github_username',
    dd.CharField(_("Github Username"), max_length=39, blank=True))
