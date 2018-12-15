# -*- coding: UTF-8 -*-
# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function


from lino.api import dd, pgettext, _


class Priorities(dd.ChoiceList):
    verbose_name = _("Priority")
    verbose_name_plural = _("Priorities")

Priorities.add_item('10', _("Critical"), 'critical')
Priorities.add_item('20', _("High"), 'high')
Priorities.add_item('30', _("Normal"), 'normal')
Priorities.add_item('40', _("Low"), 'low')
Priorities.add_item('50', _("Very Low"), 'very_low')

