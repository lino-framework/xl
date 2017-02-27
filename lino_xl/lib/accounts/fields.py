# -*- coding: UTF-8 -*-
# Copyright 2012-2015 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""
"""

from __future__ import unicode_literals

from django.db import models
from lino.core.store import BooleanStoreField
from lino.api import _

from .utils import DEBIT, CREDIT, DCLABELS


class DebitOrCreditStoreField(BooleanStoreField):

    """
    This is used as `lino_atomizer_class` for :class:`DebitOrCreditField`.
    """

    def format_value(self, ar, v):
        return unicode(DCLABELS[v])


class DebitOrCreditField(models.BooleanField):

    """A field that stores either :attr:`DEBIT
    <lino_xl.lib.accounts.utils.DEBIT>` or :attr:`CREDIT
    <lino_xl.lib.accounts.utils.CREDIT>` (see
    :mod:`lino_xl.lib.accounts.utils`).

    """
    lino_atomizer_class = DebitOrCreditStoreField

    def __init__(self, *args, **kw):
        kw.setdefault('help_text',
                      _("Debit (checked) or Credit (not checked)"))
        # kw.setdefault('default', None)
        models.BooleanField.__init__(self, *args, **kw)


