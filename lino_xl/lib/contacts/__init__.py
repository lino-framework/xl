# Copyright 2008-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""Adds functionality for managing contacts.

.. autosummary::
   :toctree:

    roles
    choicelists
    models
    utils
    mixins
    dummy
    fixtures.std
    fixtures.demo
    fixtures.demo_ee
    fixtures.demo_fr
    management.commands.garble_persons


This plugin is being extended by :ref:`welfare` in
:mod:`lino_welfare.modlib.contacts` or by :ref:`voga` in
:mod:`lino_voga.modlib.contacts`.


The default database comes with the following list of
:class:`RoleType`:

.. django2rst:: rt.show(contacts.RoleTypes)
    

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Contacts")

    needs_plugins = ['lino_xl.lib.countries', 'lino.modlib.system']

    ## settings

    region_label = _('Region')
    """The `verbose_name` of the `region` field."""

    def setup_main_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        # We use the string representations and not the classes because
        # other installed applications may want to override these tables.
        for a in ('contacts.Persons', 'contacts.Companies',
                  'contacts.Partners'):
            m.add_action(a)

    def setup_config_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('contacts.CompanyTypes')
        m.add_action('contacts.RoleTypes')

    def setup_explorer_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('contacts.Roles')



            
# @dd.when_prepared('contacts.Person', 'contacts.Company')
# def hide_region(model):
#     model.hide_elements('region')
