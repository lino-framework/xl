# Copyright 2014-2015 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Defines "parency links" between two "persons", and a user interface
to manage them.

This module is probably useful in combination with
:mod:`lino_xl.lib.households`.

.. autosummary::
   :toctree:

    choicelists
    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "Extends :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Parency links")

    ## settings
    person_model = 'contacts.Person'
    """
    A string referring to the model which represents a human in your
    application.  Default value is ``'contacts.Person'`` (referring to
    :class:`lino_xl.lib.contacts.Person`).
    """
    
    def on_site_startup(self, site):
        self.person_model = site.models.resolve(self.person_model)
        super(Plugin, self).on_site_startup(site)
        

    def setup_explorer_menu(self, site, user_type, m):
        # mg = site.plugins.contacts
        mg = site.plugins[self.person_model._meta.app_label]
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('humanlinks.Links')
        m.add_action('humanlinks.LinkTypes')


