# -*- coding: UTF-8 -*-
# Copyright 2016 Luc Saffre
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


"""

"""

from __future__ import unicode_literals

from lino.api import dd, rt, _


def objects():

    PaperType = rt.modules.sales.PaperType
    bm = rt.modules.printing.BuildMethods.get_system_default()
    yield PaperType(
        template="DefaultLetter" + bm.template_ext,
        **dd.str2kw('name', _("Letter paper")))
    yield PaperType(
        template="DefaultBlank" + bm.template_ext,
        **dd.str2kw('name', _("Blank paper")))
