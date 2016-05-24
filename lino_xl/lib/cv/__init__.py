# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Luc Saffre
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
Manage information about the *career* or *curriculum vitae* of a
person.

"""

from __future__ import unicode_literals

from lino import ad

from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Career")
    needs_plugins = ['lino.modlib.languages']

    person_model = 'contacts.Person'

    def setup_config_menu(config, site, profile, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        # m.add_action('cv.TrainingTypes')
        m.add_action('cv.StudyTypes')
        m.add_action('cv.EducationLevels')
        m.add_action('cv.Sectors')
        m.add_action('cv.Functions')
        m.add_action('cv.Regimes')
        m.add_action('cv.Statuses')
        m.add_action('cv.Durations')

    def setup_explorer_menu(config, site, profile, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        m.add_action('cv.LanguageKnowledges')
        m.add_action('cv.AllTrainings')
        m.add_action('cv.Studies')
        m.add_action('cv.Experiences')


