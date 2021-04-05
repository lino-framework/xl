# Copyright 2008-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for managing contacts.

See :doc:`/specs/contacts`.

.. autosummary::
   :toctree:

    utils
    dummy
    fixtures.demo_ee
    fixtures.demo_fr
    management.commands.garble_persons


"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Contacts")
    needs_plugins = ['lino_xl.lib.countries', 'lino.modlib.system']

    region_label = _('Region')
    """The verbose name of the :attr:`Partner.region` field."""

    use_vcard_export = False
    """Whether Lino should provide a button for exporting contact
    data as a vcf file.

    If this is `True`, Lino will install `vobject
    <http://eventable.github.io/vobject/>`__ into your Python environment.
    """

    with_roles_history = False
    """Whether we maintain a history of contact persons.

    Setting this to True will define two additional fields
    :attr:`Role.start_date` and :attr:`Role.end_date`.

    """

    def get_requirements(self, site):
        if site.plugins.contacts.use_vcard_export:
            yield 'vobject'

    def post_site_startup(self, site):
        if not site.is_installed('memo'):
            return
        rdm = site.plugins.memo.parser.register_django_model
        rdm('person', site.models.contacts.Person)
        rdm('company', site.models.contacts.Company)

    def setup_main_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        # We use the string representations and not the classes because
        # other installed applications may want to override these tables.
        for a in ('contacts.Persons', 'contacts.Companies'):
            m.add_action(a)

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('contacts.CompanyTypes')
        m.add_action('contacts.RoleTypes')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('contacts.Roles')
        m.add_action('contacts.Partners')



# @dd.when_prepared('contacts.Person', 'contacts.Company')
# def hide_region(model):
#     model.hide_elements('region')
