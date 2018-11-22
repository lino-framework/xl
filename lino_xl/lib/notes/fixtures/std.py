# -*- coding: UTF-8 -*-
# Copyright 2008-2016 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""Adds a note type "Default".

"""


from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from lino.api import rt, dd


def objects():

    NoteType = rt.models.notes.NoteType
    yield NoteType(**dd.str2kw('name', _("Default")))
    # yield noteType(
    #     _("Default"), build_method='appyodt', template='Default.odt')

