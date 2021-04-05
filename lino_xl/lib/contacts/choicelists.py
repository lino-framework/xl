# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


class PartnerEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
    max_length = 50


class CivilStates(dd.ChoiceList):
    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("Civil state")
    verbose_name_plural = _("Civil states")

add = CivilStates.add_item
add('10', _("Single"), 'single')
# add('13', _("Single cohabitating"))
# add('18', _("Single with child"))
add('20', _("Married"), 'married')
# add('21', _("Married (living alone)"))
# add('22', _("Married (living with another partner)"))
add('30', _("Widowed"), 'widowed')
# add('33', _("Widow cohabitating"))
add('40', _("Divorced"), 'divorced')
add('50', _("Separated"), 'separated')  # Getrennt von Tisch und Bett /
add('51', _("De facto separated"), 'separated_de_facto')  # Faktisch getrennt
add('60', _("Cohabitating"), 'cohabitating')


#~ '10', 'Célibataire', 'Ongehuwd', 'ledig'
#~ '13', 'Célibataire cohab.', NULL, 'ledig mit zus.',
#~ '18', 'Célibataire avec enf', NULL, 'ledig mit kind',
#~ '20', 'Marié', 'Gehuwd', 'verheiratet',
#~ '21', 'Séparé de fait', NULL, 'verheiratet alleine',
#~ '22', 'Séparé de fait cohab', NULL, 'verheiratet zus.',
#~ '30', 'Veuf(ve)', NULL, 'Witwe(r)',
#~ '33', 'Veuf(ve) cohab.', NULL, 'Witwe(r) zus.',
#~ '40', 'Divorcé', NULL, 'geschieden',
#~ '50', 'séparé(e) de corps', NULL, 'von Tisch & Bet get.',


