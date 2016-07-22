# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
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
"""
Database models for `lino_xl.lib.notes`.

.. autosummary::

"""

from django.conf import settings
from lino.api import dd, rt
from lino.modlib.notify.mixins import Observable


class Notable(Observable):
    """An :class:`lino.modlib.notify.mixins.Observable` which additionally"""
    class Meta:
        abstract = True

    def get_system_note_type(self, request):
        """Expected to return either `None` (the default) or an existing
        :class:`NoteType <lino_xl.lib.notes.models.NoteType>`
        instance. If this is not `None`, then the system note will be
        stored in the database as a
        :class:`lino_xl.lib.notes.models.Note`.

        """
        return settings.SITE.site_config.system_note_type

    def add_system_note(self, ar, owner, subject, body,
                        silent=False, **kw):
        """Create a system note and emit notifications."""
        # dd.logger.info("20160718 %s add_system_note()", self)
        nt = self.get_system_note_type(ar)
        if not nt:
            # dd.logger.info("20160718 not system_note_type")
            return
        prj = owner.get_related_project()
        if prj:
            kw.update(project=prj)
        note = rt.models.notes.Note(
            event_type=nt, owner=owner,
            subject=subject, body=body, user=ar.user, **kw)
        # owner.update_system_note(note)
        note.save()
        self.emit_notification(ar, owner, subject, body)
        # sender = request.user.email or settings.SERVER_EMAIL
        # if not sender or '@example.com' in sender:
        #     return
        # recipients = owner.get_notify_observers(request)
        # dd.send_email(subject, sender, body, recipients)

