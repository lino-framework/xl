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

    if False:

        guest_role = Instantiator('cal.GuestRole').build
        yield guest_role(**dd.babel_values('name',
                                           de=u"Teilnehmer",
                                           fr=u"Participant",
                                           en=u"Participant",
                                           et=u"Osavõtja",
                                       ))
        yield guest_role(**dd.babel_values('name',
                                           de=u"Reiseführer",
                                           fr=u"Guide",
                                           en=u"Guide",
                                           et=u"Reisijuht",
                                       ))
        yield guest_role(**dd.babel_values('name',
                                           de=u"Vorsitzender",
                                           fr=u"Président",
                                           en=u"Presider",
                                           et=u"Eesistuja",
                                        ))
        yield guest_role(**dd.babel_values('name',
                                           de=u"Protokollführer",
                                           fr=u"Greffier",
                                           en=u"Reporter",
                                           et=u"Sekretär",
                                       ))

    if False:

        place = Instantiator('cal.Room').build
        yield place(**dd.babel_values('name',
                                      de=u"Büro",
                                      fr=u"Bureau",
                                      en=u"Office",
                                  ))
        yield place(**dd.babel_values('name',
                                      de=u"Beim Klienten",
                                      fr=u"Chez le client",
                                      en=u"A the client's",
                                  ))
        yield place(**dd.babel_values('name',
                                      de=u"beim Arbeitgeber",
                                      fr=u"chez l'employeur",
                                      en=u"at employer's",
                                  ))
