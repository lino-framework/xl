# Copyright 2008-2015 Luc Saffre
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

"""Choicelists for `lino_xl.lib.finan`.

"""

from lino.api import dd, _


# class VoucherStates(dd.Workflow):
#     """The list of possible states for a voucher."""
#     @classmethod
#     def get_editable_states(cls):
#         return [o for o in cls.objects() if o.editable]

# add = VoucherStates.add_item
# add('10', _("Draft"), 'draft', editable=True)
# add('20', _("Registered"), 'registered', editable=False)


# @dd.receiver(dd.pre_analyze)
# def setup_workflow(sender=None, **kw):
#     VoucherStates.registered.add_transition(
#         _("Register"), states='draft', icon_name='accept')
#     VoucherStates.draft.add_transition(
#         _("Deregister"), states="registered", icon_name='pencil')


