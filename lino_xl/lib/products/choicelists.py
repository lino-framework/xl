# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Choicelists for `lino_xl.lib.products`.

"""

from lino.api import dd, _


class DeliveryUnit(dd.Workflow):
    """The list of possible delivery units of a product."""
    verbose_name = _("Delivery unit")
    verbose_name_plural = _("Delivery units")
    pass

add = DeliveryUnit.add_item
add('10', _("Hour"), 'hour')
add('20', _("Piece"), 'piece')
add('30', _("Kg"), 'kg')


