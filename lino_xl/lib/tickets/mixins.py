# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _
from lino_xl.lib.votes.choicelists import VoteStates
from lino_xl.lib.stars.mixins import get_favourite

class Milestone(dd.Model):
    """Base class for models that can be used as
    :attr:`lino_xl.lib.tickets.Plugin.milestone_model`.

    """
    class Meta(object):
        abstract = True

    def get_milestone_users(self):
        return []
    
    def after_ui_save(self, ar, cw):
        """
        """
        # super(Milestone, self).after_ui_save(ar, cw)
        # participants = list(self.get_milestone_users())
        # for wish in self.wishes_by_milestone.all():
        #     for user in participants:
        #         if dd.is_installed('votes'):
        #             wish.ticket.set_auto_vote(user, VoteStates.invited)
        #         if dd.is_installed('stars'):
        #             star = get_favourite(wish.ticket, user=user)
        #             if star is None:
        #                 Star = rt.models.stars.Star
        #                 star = Star(owner=wish.ticket, user=user)
        #                 star.save()

