# Copyright 2008-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.api import ad, _
# from lino_xl.lib.contacts import Plugin
# from lino.modlib.users import Plugin

class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Google API People")
    # partner_model = 'googleapi_people.Person'
    # extends_models = ['Person']

    # needs_plugins = ['lino_xl.lib.contacts']

    ## settings

    path_googleapi_client_secret_file = 'client_secret.json'
    """The `path` to the GoogleAPI secret file client_secret.json."""
    googleapi_people_scopes = ['https://www.googleapis.com/auth/contacts',
                               'https://www.googleapis.com/auth/contacts.readonly',
                               'https://www.googleapis.com/auth/plus.login',
                               'https://www.googleapis.com/auth/user.addresses.read',
                               'https://www.googleapis.com/auth/user.birthday.read',
                               'https://www.googleapis.com/auth/user.emails.read',
                               'https://www.googleapis.com/auth/user.phonenumbers.read',
                               'https://www.googleapis.com/auth/userinfo.email',
                               'https://www.googleapis.com/auth/userinfo.profile']
    """ GoogleAPi Scopes """
    googleapi_application_name = False
    """ The Application's name defined in the gogole API Console"""


    # def post_site_startup(self, site):
    #     self.partner_model = site.models.resolve(self.partner_model)
    #     rdm = site.plugins.memo.parser.register_django_model
    #     rdm('partner', site.models.googleapi_people.Partner)
    #     super(Plugin, self).on_site_startup(site)
    #     rdm('company', site.models.contacts.Company)

    # def setup_main_menu(self, site, user_type, m):
    #     m = m.add_menu(self.app_label, self.verbose_name)
    #     We use the string representations and not the classes because
    #     other installed applications may want to override these tables.
    # for a in ('contacts.Persons', 'contacts.Companies'):
    #     m.add_action(a)
    #
    # def setup_config_menu(self, site, user_type, m):
    #     m = m.add_menu(self.app_label, self.verbose_name)
    #     m.add_action('contacts.CompanyTypes')
    #     m.add_action('contacts.RoleTypes')
    #
    # def setup_explorer_menu(self, site, user_type, m):
    #     m = m.add_menu(self.app_label, self.verbose_name)
    #     m.add_action('contacts.Roles')
    #     m.add_action('contacts.Partners')

# @dd.when_prepared('contacts.Person', 'contacts.Company')
# def hide_region(model):
#     model.hide_elements('region')
