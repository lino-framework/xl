# -*- coding: UTF-8 -*-
# Copyright 2016-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
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
    column_names = "value name text table_name *"

    @dd.virtualfield(models.CharField(_("Table name")))
    def table_name(cls, choice, ar):
        return choice.table_name


add = ProductTypes.add_item
add('100', _("Products"), 'default')


class PriceFactor(dd.Choice):
    field_cls = None
    def __init__(self, value, cls, name):
        self.field_cls = cls
        self.field_name = 'pf_' + name
        super(PriceFactor, self).__init__(value, cls.verbose_name, name)

class PriceFactors(dd.ChoiceList):
    item_class = PriceFactor
    verbose_name = _("Price factor")
    verbose_name_plural = _("Price factors")


