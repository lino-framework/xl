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
    properties = dd.resolve_app('properties')
    yield ptype(id=1, **dd.babel_values('name', **dict(
        en="Present or not",
        de=u"Vorhanden oder nicht",
        fr=u"Présent ou pas",
        et=u"Olemas või mitte",
        nl=u"Ja of niet",
    )))
    yield ptype(id=2,
                choicelist=properties.HowWell.actor_id,
                default_value=properties.HowWell.default.value,
                **dd.babel_values('name', **dict(
                    en="Rating",
                    de=u"Bewertung",
                    et=u"Hinnang",
                    fr=u"Appréciation(?)",
                    nl=u"Hoe goed",
                )))
