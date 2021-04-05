# -*- coding: UTF-8 -*-
# Copyright 2008-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Database fields for `lino_xl.lib.ledger`.

"""

from django.db import models
from lino.api import dd, _
from lino.core.store import BooleanStoreField
# from .utils import DCLABELS
from .choicelists import DC


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

    When the amount is positive and dc is DC.debit, return None.
    When the amount is positive and dc is DC.credit, return amount.
    When the amount is negative and dc is DC.debit, return -amount.
    When the amount is negative and dc is DC.credit, return None.

    """

    editable = True
    empty_values = set([None])

    def __init__(self, dc, *args, **kwargs):
        self.dc = dc
        kwargs.update(blank=True)
        dd.VirtualField.__init__(self, dd.PriceField(*args, **kwargs), None)

    def set_value_in_object(self, request, obj, value):
        if not value:
            obj.amount = None
        elif self.dc == DC.debit:
            obj.amount = -value
        else:
            obj.amount = value

    def value_from_object(self, obj, ar):
        if self.dc == DC.debit:
            return -obj.amount if obj.amount < 0 else None
        return obj.amount if obj.amount > 0 else None


# class DebitOrCreditStoreField(BooleanStoreField):
#
#     def format_value(self, ar, v):
#         return str(DCLABELS[v])
#
#
# class DebitOrCreditField(models.BooleanField):
#
#     lino_atomizer_class = DebitOrCreditStoreField
#
#     def __init__(self, *args, **kw):
#         kw.setdefault('help_text',
#                       _("Debit (not checked) or Credit (checked)"))
#         # kw.setdefault('default', None)
#         models.BooleanField.__init__(self, *args, **kw)
#
