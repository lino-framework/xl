# -*- coding: UTF-8 -*-
# Copyright 2011-2015 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)
"Choicelists for :mod:`lino_xl.lib.outbox`."

from django.utils.translation import gettext_lazy as _
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


