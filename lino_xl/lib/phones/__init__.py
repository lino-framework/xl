# Copyright 2017 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds models and methods to handle multiple phone numbers, email
addresses etc ("contact details") per partner. See
:doc:`/specs/phones`.

.. autosummary::
   :toctree:

    fixtures.demo2

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Contact Details")
    partner_model = 'contacts.Partner'

    def on_site_startup(self, site):
        super(Plugin, self).on_site_startup(site)
        if self.partner_model is None:
            return
        self.partner_model = site.models.resolve(self.partner_model)
        
        from lino.mixins import Phonable
        if not issubclass(self.partner_model, Phonable):
            raise Exception("partner_model {} is not a Phonable".format(
                self.partner_model))
        
    def setup_explorer_menu(self, site, user_type, m):
        # mg = self.get_menu_group()
        mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('phones.ContactDetailTypes')
        m.add_action('phones.ContactDetails')

