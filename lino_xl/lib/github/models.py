# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""Database models for this plugin.
"""

from lino.api import dd, rt, _
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

    user_name = dd.CharField(_("User Name"))
    repo_name = dd.CharField(_("Repository Name"))
    o_auth    = dd.CharField(_("OAuth Token"),
                             blank=True)

    def __str__(self):
        return "%s:%s"%(self.user_name, self.repo_name)

    @dd.displayfield(_("Url"))
    def url(self, ar):
        return "https://api.github.com/repos/%s/%s/"%(self.user_name,
                                                      self.repo_name)

class Commit(Created):
    """A **Commit** is a git commit sha and other relevant data.

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
    git_user = dd.CharField(_("Git User Name"),
                            blank=True)
    sha = dd.CharField(_("Sha Hash"),
                       max_length=40)
    url = dd.CharField(_("Commit page"))
    summary = dd.CharField(_("Summary"))


dd.inject_field(
    "users.User", 'git_username',
    dd.CharField(_("Github Username"), blank=True))
