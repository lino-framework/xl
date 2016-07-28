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
Defines actions used by this plugin.

"""

from lino.modlib.notify.actions import NotifyingAction


class NotableAction(NotifyingAction):
    """Abstract base class for notifying actions that may create a system
    note and a notification.

    """
    def emit_notification(self, ar, owner, **kw):
        kw.update(
            subject=ar.action_param_values.notify_subject,
            body=ar.action_param_values.notify_body)
        owner.emit_system_note(ar, **kw)
        super(NotableAction, self).emit_notification(ar, owner, **kw)


