# -*- coding: UTF-8 -*-
# Copyright 2011-2015 Luc Saffre
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
"Choicelists for :mod:`lino_xl.lib.outbox`."

from django.utils.translation import ugettext_lazy as _
from lino.api import dd


class RecipientTypes(dd.ChoiceList):

    """A list of possible values for the `type` field of a
    :class:`Recipient`.

    """
    verbose_name = _("Recipient Type")

add = RecipientTypes.add_item
add('to', _("to"), 'to')
add('cc', _("cc"), 'cc')
add('bcc', _("bcc"), 'bcc')
#~ add('snail',_("Snail mail"),'snail')


