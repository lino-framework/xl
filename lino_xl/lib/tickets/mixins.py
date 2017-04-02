# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _
from lino_xl.lib.votes.choicelists import VoteStates

class Milestone(dd.Model):
    """Base class for models that can be used as
    :attr:`lino_xl.lib.tickets.Plugin.milestone_model`.

    """
    class Meta(object):
        abstract = True

    def get_milestone_users(self):
        return []
    
    def after_ui_save(self, ar, cw):
        """Automatically invite every participant to vote on every wish.

        """
        super(Milestone, self).after_ui_save(ar, cw)
        participants = self.get_milestone_users()
        for wish in self.wishes_by_milestone.all():
            for user in participants:
                wish.ticket.set_auto_vote(user, VoteStates.invited)
        
    
