# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
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

Default data for `pages` is the content defined in 
:mod:`lino_xl.lib.pages.fixtures.web`.

"""
#~ from lino_xl.lib.pages.fixtures.web import objects


def objects():

    from lino_xl.lib.pages.fixtures.intro import objects
    yield objects()

    #~ from lino_xl.lib.pages.fixtures.man import objects
    #~ yield objects()
