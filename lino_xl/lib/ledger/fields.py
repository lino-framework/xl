# -*- coding: UTF-8 -*-
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


"""Database fields for `lino_xl.lib.ledger`.


"""

from lino.api import dd, _


# def MatchField(verbose_name=None, **kwargs):
#     """A pointer to another movement which is to be cleared by the owner
#     of this field.

#     """
#     if verbose_name is None:
#         verbose_name = _("Match")
#     kwargs.update(verbose_name=verbose_name)
#     kwargs.update(help_text=_("The movement to be cleared."))
#     kwargs.update(related_name="%(app_label)s_%(class)s_set_by_match",)
#     return dd.ForeignKey('ledger.Movement', **kwargs)


# class MatchField(models.CharField):

#     def __init__(self, verbose_name=None, **kw):
#         if verbose_name is None:
#             verbose_name = _("Match")
#         kw.setdefault('max_length', 20)
#         models.CharField.__init__(self, verbose_name, **kw)


class DcAmountField(dd.VirtualField):
    """An editable virtual PriceField to get and set both database fields
    :attr:`amount` and :attr:`dc` at once. It may be used only on
    models which also defines these two fields.

    """

    editable = True
    empty_values = set([None])

    def __init__(self, dc, *args, **kwargs):
        self.dc = dc
        kwargs.update(blank=True)
        dd.VirtualField.__init__(self, dd.PriceField(*args, **kwargs), None)

    def set_value_in_object(self, request, obj, value):
        obj.amount = value
        obj.dc = self.dc

    def value_from_object(self, obj, ar):
        if obj.dc == self.dc:
            return obj.amount
        return None
