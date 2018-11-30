# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.api import dd, _


class DeliveryUnits(dd.ChoiceList):
    verbose_name = _("Delivery unit")
    verbose_name_plural = _("Delivery units")

add = DeliveryUnits.add_item
add('10', _("Hour"), 'hour')
add('20', _("Piece"), 'piece')
add('30', _("Kg"), 'kg')


class ProductType(dd.Choice):
    table_name = 'products.Products'

class ProductTypes(dd.ChoiceList):
    item_class = ProductType
    verbose_name = _("Product type")
    verbose_name_plural = _("Product types")

add = ProductTypes.add_item
add('100', _("Products"), 'default')
