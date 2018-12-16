# -*- coding: UTF-8 -*-
# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function


from lino.api import dd, pgettext, _


class Priorities(dd.ChoiceList):
    verbose_name = _("Priority")
    verbose_name_plural = _("Priorities")


Priorities.add_item('10', pgettext("priority", "Critical"), 'critical')
Priorities.add_item('20', pgettext("priority", "High"), 'high')
Priorities.add_item('30', pgettext("priority", "Normal"), 'normal')
Priorities.add_item('40', pgettext("priority", "Low"), 'low')
Priorities.add_item('50', pgettext("priority", "Very Low"), 'very_low')

