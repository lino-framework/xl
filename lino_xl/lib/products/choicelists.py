# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
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






from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd
from lino import mixins
