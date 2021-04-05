# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Some standard workflow definition modules for :mod:`lino_xl.lib.cal`.

"""


from django.conf import settings
from lino.api import _

from lino_xl.lib.cal.choicelists import TaskStates


def f(name):
    if settings.SITE.use_silk_icons:
        return name

TaskStates.todo.add_transition(
    _("Reopen"), required_states='done cancelled important')
TaskStates.done.add_transition(
    required_states='todo started important', icon_name=f('accept'))
TaskStates.cancelled.add_transition(
    required_states='todo started important', icon_name=f('cancel'))
TaskStates.important.add_transition(
    required_states='todo started', icon_name=f('lightning'))
