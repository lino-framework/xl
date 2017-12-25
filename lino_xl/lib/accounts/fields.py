# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str

from django.db import models
from lino.core.store import BooleanStoreField
from lino.api import _

from .utils import DEBIT, CREDIT, DCLABELS


class DebitOrCreditStoreField(BooleanStoreField):

    def format_value(self, ar, v):
        return str(DCLABELS[v])


class DebitOrCreditField(models.BooleanField):

    lino_atomizer_class = DebitOrCreditStoreField

    def __init__(self, *args, **kw):
        kw.setdefault('help_text',
                      _("Debit (checked) or Credit (not checked)"))
        # kw.setdefault('default', None)
        models.BooleanField.__init__(self, *args, **kw)


