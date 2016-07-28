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

import logging
logger = logging.getLogger(__name__)

from django.conf import settings

from lino.api import rt

from lino.modlib.notify.actions import NotifyingAction


class NotableAction(NotifyingAction):

    def get_system_note_type(self, ar):
        """Expected to return either `None` (the default) or an existing
        :class:`NoteType <lino_xl.lib.notes.models.NoteType>`
        instance. If this is not `None`, then a notification will
        still be emitted, but the system not will not be stored in the
        database as a :class:`lino_xl.lib.notes.models.Note`.

        """
        return settings.SITE.site_config.system_note_type

    def emit_notification(self, ar, **kw):
        nt = self.get_system_note_type(ar)
        if nt:
            obj = ar.selected_rows[0]
            owner = self.get_notify_owner(obj)
            prj = owner.get_related_project()
            if prj:
                kw.update(project=prj)
            note = rt.models.notes.Note(
                event_type=nt, owner=owner,
                subject=ar.action_param_values.notify_subject,
                body=ar.action_param_values.notify_body,
                user=ar.user, **kw)
            note.save()

        super(NotableAction, self).emit_notification(ar, **kw)

