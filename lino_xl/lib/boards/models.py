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
"""Database models for `lino.modlib.boards`.

"""


from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


from lino.api import dd
from lino import mixins
from django.utils.translation import ugettext_lazy as _

from lino.modlib.office.roles import OfficeUser

from .mixins import BoardDecision


class Board(mixins.BabelNamed, mixins.DatePeriod):

    class Meta:
        app_label = 'boards'
        verbose_name = _("Board")
        verbose_name_plural = _("Boards")

    def full_clean(self, *args, **kw):
        if not self.start_date:
            self.start_date = dd.today()
        super(Board, self).full_clean(*args, **kw)


dd.update_field(
    Board, 'start_date',
    verbose_name=_("Works since"),
    null=False)
dd.update_field(Board, 'end_date', verbose_name=_("Worked until"))


class Boards(dd.Table):
    model = 'boards.Board'
    required_roles = dd.required(dd.SiteStaff, OfficeUser)
    column_names = 'name *'
    order_by = ["name"]

    insert_layout = """
    name
    """

    detail_layout = """
    id name
    boards.MembersByBoard
    """


class Member(dd.Model):
    """A Member is when a given :class:`ml.contacts.Person`
    belongs to a given :class:`Board`.

    .. attribute:: board

    Pointer to the :class:`Board`.

    .. attribute:: person

    Pointer to the :class:`ml.contacts.Person`.

    .. attribute:: role

    What the person is supposed to do in this board.  Pointer to the
    :class:`ml.contacts.RoleType`.
    """
    class Meta:
        app_label = 'boards'
        verbose_name = _("Board member")
        verbose_name_plural = _("Board members")

    board = dd.ForeignKey('boards.Board')
    person = dd.ForeignKey("contacts.Person")
    role = dd.ForeignKey(
        "contacts.RoleType", blank=True, null=True)


class Members(dd.Table):
    model = 'boards.Member'
    required_roles = dd.required(dd.SiteStaff, OfficeUser)


class MembersByBoard(Members):
    master_key = 'board'
    column_names = "role person"
    order_by = ["role"]


