# coding: UTF-8
# Copyright 2011-2016 Luc Saffre
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
"""Database models for `lino_xl.lib.thirds`.

"""

from builtins import str
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from lino.api import dd
from lino import mixins
from lino_xl.lib.contacts import models as contacts
from lino.modlib.gfks.mixins import Controllable


@dd.python_2_unicode_compatible
class Third(mixins.Sequenced, contacts.PartnerDocument, Controllable):

    class Meta:
        verbose_name = _("Third Party")
        verbose_name_plural = _('Third Parties')

    remark = models.TextField(_("Remark"), blank=True, null=True)

    def summary_row(self, ar, **kw):
        #~ s = ui.href_to(self)
        return ["(", unicode(self.seqno), ") "] + list(contacts.PartnerDocument.summary_row(self, ar, **kw))

    def __str__(self):
        return str(self.seqno)
        #~ return unicode(self.get_partner())


class Thirds(dd.Table):
    model = Third
    #~ order_by = ["modified"]
    column_names = "owner_type owner_id seqno person company *"


class ThirdsByController(Thirds):
    master_key = 'owner'
    column_names = "seqno person company id *"
    slave_grid_format = 'summary'
