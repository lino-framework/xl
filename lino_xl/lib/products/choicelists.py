# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Choicelists for `lino_xl.lib.products`.

"""

from lino.api import dd, _


class DeliveryUnit(dd.ChoiceList):
    """The list of possible delivery units of a product."""
    verbose_name = _("Delivery unit")
    verbose_name_plural = _("Delivery units")

add = DeliveryUnit.add_item
add('10', _("Hour"), 'hour')
add('20', _("Piece"), 'piece')
add('30', _("Kg"), 'kg')


class ProductTypes(dd.ChoiceList):
    verbose_name = _("Product type")
    verbose_name_plural = _("Product types")

add = ProductTypes.add_item
add('100', _("Default"), 'default')
