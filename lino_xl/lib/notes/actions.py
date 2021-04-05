# -*- coding: UTF-8 -*-
# Copyright 2009-2018 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Defines actions used by this plugin.

"""

# from lino.modlib.notify.actions import NotifyingAction


# class NotableAction(NotifyingAction):
#     """
#     Abstract base class for notifying actions that may create a system
#     note and a notification.
#     """
#     def emit_message(self, ar, owner, **kw):
#         kw.update(
#             subject=ar.action_param_values.notify_subject,
#             body=ar.action_param_values.notify_body)
#         owner.emit_system_note(ar, **kw)
#         super(NotableAction, self).emit_message(ar, owner, **kw)


