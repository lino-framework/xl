# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
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
This defines the :class:`Shortcuts` choicelist.

"""

from __future__ import unicode_literals
from __future__ import print_function

from django.utils.translation import ugettext_lazy as _

from lino.api import dd


class Shortcut(dd.Choice):
    model_spec = None

    def __init__(self, model_spec, name, verbose_name):
        self.model_spec = model_spec
        value = model_spec + "." + name
        super(Shortcut, self).__init__(value, verbose_name, name)


class Shortcuts(dd.ChoiceList):
    """The list of excerpt shortcut fields.  An excerpt shortcut field is
a virtual display field with actions for quickly managing, from a
given database object, the excerpt for this object of a given type.

These virtual fields are being installed during pre_analyze by
:func:`lino_xl.lib.excerpts.models.set_excerpts_actions`.

    """
    verbose_name = _("Excerpt shortcut")
    verbose_name_plural = _("Excerpt shortcuts")
    item_class = Shortcut
    max_length = 50  # fields get created before the values are known
