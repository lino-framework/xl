# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for managing households (i.e. groups of humans
who live together in a same house).

See :doc:`/specs/households`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "Extends :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Households")

    person_model = "contacts.Person"
    """A string referring to the model which represents a human in your
    application.  Default value is ``'contacts.Person'`` (referring to
    :class:`lino_xl.lib.contacts.models.Person`).

    """

    adult_age = 18
    """The age (in years) a person needs to have in order to be considered
    adult."""
    # adult_age = datetime.timedelta(days=18*365)
    
    def on_site_startup(self, site):
        self.person_model = site.models.resolve(self.person_model)
        super(Plugin, self).on_site_startup(site)
        
    def post_site_startup(self, site):
        if not site.is_installed('memo'):
            return

        rdm = site.plugins.memo.parser.register_django_model
        rdm('household', site.models.households.Household)
    
    def setup_main_menu(config, site, user_type, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        m.add_action('households.Households')

    def setup_config_menu(config, site, user_type, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        # m.add_action(Roles)
        m.add_action('households.Types')

    def setup_explorer_menu(config, site, user_type, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        m.add_action('households.MemberRoles')
        m.add_action('households.Members')
