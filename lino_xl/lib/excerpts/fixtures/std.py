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

"""Creates a certifying :class:`ExcerptType` instance for every model
which inherits from :class:`Certifiable`.

"""

from django.contrib.contenttypes.models import ContentType

from lino.api import dd, rt
from lino_xl.lib.excerpts.mixins import Certifiable


def objects():
    ExcerptType = rt.modules.excerpts.ExcerptType
    for cls in rt.models_by_base(Certifiable):
        kw = dd.str2kw('name', cls._meta.verbose_name)
        if False:
            kw.update(backward_compat=True)
        yield ExcerptType(
            #template='Default.odt',
            primary=True,
            certifying=True,
            content_type=ContentType.objects.get_for_model(cls),
            **kw)

