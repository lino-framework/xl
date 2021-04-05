# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Defines the default workflows for applications which use reception
plugin.

This can be used as :attr:`workflows_module
<lino.core.site.Site.workflows_module>`

"""

from __future__ import unicode_literals

import datetime
from builtins import str

from lino_xl.lib.cal.workflows import *
from lino_xl.lib.cal.workflows import feedback
from lino_xl.lib.reception.models import checkout_guest

from django.utils.translation import gettext_lazy as _
# from django.utils.translation import pgettext_lazy as pgettext

from .models import GuestStates
from .models import EntryStates


class CloseMeeting(feedback.CloseMeeting):
    """Close the meeting (mark it as "took place") and check out all
    guests. Ask confirmation naming the guests who need to check out.

    """
    def execute(self, ar, obj):

        guests = obj.guest_set.filter(gone_since__isnull=True,
                                      waiting_since__isnull=False)
        def yes(ar):
            if not obj.end_time:
                obj.end_time = datetime.datetime.now()
                ar.info("event.end_time has been set by CloseMeeting")
            for g in guests:
                checkout_guest(g, ar)
            return super(CloseMeeting, self).execute(ar, obj)

        num = len(guests)
        if num == 0:
            return yes(ar)  # no confirmation
        msg = _("This will checkout {num} guests: {guests}.").format(
            num=num,
            guests=', '.join([str(g.partner) for g in guests]))
        return ar.confirm(yes, msg, _("Are you sure?"))


EntryStates.override_transition(close_meeting=CloseMeeting)
