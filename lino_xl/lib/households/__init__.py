# -*- coding: UTF-8 -*-
# Copyright 2014-2015 Luc Saffre
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

"""Adds functionality for managing households (i.e. groups of humans
who live together in a same house).

Technical specification see :ref:`lino.specs.households`.

.. autosummary::
   :toctree:

    models
    choicelists
    fixtures.std
    fixtures.demo

This plugin is being extended by :ref:`welfare` in
:mod:`lino_welfare.modlib.households`.

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

    def setup_main_menu(config, site, profile, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        m.add_action('households.Households')

    def setup_config_menu(config, site, profile, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        # m.add_action(Roles)
        m.add_action('households.Types')

    def setup_explorer_menu(config, site, profile, m):
        mnugrp = site.plugins.contacts
        m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
        m.add_action('households.MemberRoles')
        m.add_action('households.Members')
