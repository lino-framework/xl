# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

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

    def on_site_startup(self, site):
        self.person_model = site.models.resolve(self.person_model)
        super(Plugin, self).on_site_startup(site)
        
    def setup_config_menu(config, site, user_type, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        # m.add_action('cv.TrainingTypes')
        m.add_action('cv.StudyTypes')
        m.add_action('cv.EducationLevels')
        m.add_action('cv.Sectors')
        m.add_action('cv.Functions')
        m.add_action('cv.Regimes')
        m.add_action('cv.Statuses')
        m.add_action('cv.Durations')

    def setup_explorer_menu(config, site, user_type, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        m.add_action('cv.AllLanguageKnowledges')
        m.add_action('cv.AllTrainings')
        m.add_action('cv.Studies')
        m.add_action('cv.Experiences')


