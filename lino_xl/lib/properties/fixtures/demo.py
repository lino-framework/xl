# -*- coding: UTF-8 -*-
# Copyright 2011-2014 Luc Saffre
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


from django.utils.translation import ugettext as _

from lino.utils.instantiator import Instantiator
from lino.api import dd


def objects():
    ptype = Instantiator('properties.PropType').build

    division = ptype(
        **dd.babel_values('name', **dict(
            en="Division", fr="Division", de=u"Abteilung")))
    yield division
    divchoice = Instantiator(
        'properties.PropChoice', 'value', type=division).build
    yield divchoice('1', **dd.babel_values(
        'text', **dict(en="Furniture", de=u"Möbel", fr=u"Meubles")))
    yield divchoice('2', **dd.babel_values(
        'text', **dict(en="Web hosting", de=u"Hosting", fr=u"Hosting")))
