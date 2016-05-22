# Copyright 2008-2015 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.
"""Model mixins for `lino.modlib.boards`.

"""


from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


from lino.api import dd, rt, _
from django.db import models

from lino.modlib.users.mixins import UserAuthored


class BoardDecision(UserAuthored):
    """Mixin for models that represent a board decision.  Base class for
    :class:`lino_welfare.modlib.aids.mixins.Confirmation`.

    """
    class Meta:
        abstract = True

    decision_date = models.DateField(
        verbose_name=_('Decided'), blank=True, null=True)
    board = models.ForeignKey('boards.Board', blank=True, null=True)

    @dd.chooser()
    def board_choices(self, decision_date):
        qs = rt.modules.boards.Board.objects.all()
        if decision_date:
            qs = dd.PeriodEvents.active.add_filter(qs, decision_date)
        return qs

