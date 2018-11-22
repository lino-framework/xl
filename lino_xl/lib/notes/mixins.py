# -*- coding: UTF-8 -*-
# Copyright 2009-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

from django.conf import settings

from lino.api import dd, rt


class Notable(dd.Model):
    """
    Base class for models which can emit system notes.
    """
    class Meta(object):
        abstract = True

    def get_system_note_type(self, ar):
        """
        Expected to return either `None` (the default) or an existing
        :class:`EventType <lino_xl.lib.notes.models.EventType>`
        instance. If this is not `None`, then a notification will
        still be emitted, but the system not will not be stored in the
        database as a :class:`lino_xl.lib.notes.models.Note`.
        """
        return settings.SITE.site_config.system_note_type

    def emit_system_note(self, ar, **kw):
        nt = self.get_system_note_type(ar)
        if nt:
            # obj = ar.selected_rows[0]
            # owner = self.get_notify_owner(obj)
            prj = self.get_related_project()
            if prj:
                kw.update(project=prj)
            note = rt.models.notes.Note(
                event_type=nt, owner=self,
                user=ar.user, **kw)
            note.full_clean()
            note.save()


