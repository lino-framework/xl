# -*- coding: UTF-8 -*-
# Copyright 2015-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _


class SpecialType(dd.Choice):

    def get_notes(self, **kw):
        """Return a queryset with the uploads of this shortcut."""
        return rt.models.notes.Note.objects.filter(
            type__special_type=self, **kw)


class SpecialTypes(dd.ChoiceList):
    verbose_name = _("Special note type")
    verbose_name_plural = _("Special note types")
    item_class = SpecialType
    max_length = 5

