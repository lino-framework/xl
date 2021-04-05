# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.conf import settings
from lino.api import dd, rt
from lino.utils import Cycler


def objects():

    polls = rt.models.polls

    USERS = Cycler(settings.SITE.user_model.objects.all())

    for p in polls.Poll.objects.exclude(questions_to_add=''):
        p.after_ui_save(None, None)
        yield polls.Response(
            poll=p, user=USERS.pop(), date=dd.today(),
            state=polls.ResponseStates.draft)
