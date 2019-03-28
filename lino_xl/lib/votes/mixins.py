# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Model mixins for this plugin.
"""

from lino.api import dd, rt, _
from lino.utils.instantiator import create_row, create_or_update_row
from lino.modlib.notify.mixins import ChangeNotifier
from .choicelists import VoteStates
from .roles import SimpleVotesUser
from .actions import CreateVote, EditVote, VotableEditVote

class Votable(ChangeNotifier):
    """Base class for models that can be used as
    :attr:`lino_xl.lib.votes.Plugin.votable_model`.

    """
    class Meta(object):
        abstract = True

    if dd.is_installed('votes'):
    
        create_vote = CreateVote()
        edit_vote = VotableEditVote()

        # def get_project_for_vote(self, vote):
        #     return None

        def get_vote_raters(self):
            """Yield or return a list of the users who are allowed to rate the
            votes on this votable.

            Lino automatically (in :meth:`after_ui_save`) creates an
            **author vote** for each of them.

            """
            return []

        def get_favourite(self, user):
            """Return the vote of the given user about this votable, or None if no
    vote exists.

            There should be either 0 or 1 vote per user and votable.

            """
            qs = rt.models.votes.Vote.objects.filter(
                votable=self, user=user)
            if qs.count() == 0:
                return None
            return qs[0]

        def get_change_observers(self, ar=None):
            for x in super(Votable, self).get_change_observers(ar):
                yield x
            for vote in rt.models.votes.Vote.objects.filter(votable=self):
                yield (vote.user, vote.mail_mode or vote.user.mail_mode)

        def set_author_votes(self):
            """Verify that every vote rater has a vote.

            The raters of a vote are returned by :meth:`get_vote_raters`.

            """
            # wanted_votes = dict()
            # def collect(user, state):
            #     if user in wanted_votes:
            #         return
            for user in self.get_vote_raters():
                create_or_update_row(
                    rt.models.votes.Vote,
                    dict(user=user,
                         votable=self),
                    dict(user=user,
                         votable=self,
                         state=VoteStates.author)
                )

            # for user, state in wanted_votes.items():
            #     self.set_auto_vote(user, state)

        # def on_commented(self, comment, ar, cw):
        #     super(Votable, self).on_commented(comment, ar, cw)
        #     self.set_auto_vote(comment.user, VoteStates.invited)

        def set_auto_vote(self, user, state):
            # dd.logger.info("20170406 set_auto_vote %s %s", user, state)
            vote = self.get_favourite(user)
            if vote is None:
                create_row(
                    rt.models.votes.Vote, user=user,
                    votable=self, state=state)

        def after_ui_create(self, ar):
            """Automatically call :meth:`set_author_votes` after creation.

            """
            super(Votable, self).after_ui_create(ar)
            self.set_author_votes()
