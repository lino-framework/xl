# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from lino.modlib.system.choicelists import ObservedEvent
from lino.api import dd, _

from .utils import only_coached_on

from lino_xl.lib.clients.choicelists import ClientEvents


# class ClientIsActive(ObservedEvent):
#     text = _("Active")

#     def add_filter(self, qs, pv):
#         period = (pv.start_date, pv.end_date)
#         qs = only_coached_on(qs, period)
#         return qs

# ClientEvents.add_item_instance(ClientIsActive("active"))


class ClientHasCoaching(ObservedEvent):
    text = _("Coaching")

    def add_filter(self, qs, pv):
        period = (pv.start_date, pv.end_date)
        qs = only_coached_on(qs, period)
        return qs

ClientEvents.add_item_instance(ClientHasCoaching("active"))

