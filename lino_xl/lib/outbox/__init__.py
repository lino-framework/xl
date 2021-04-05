# Copyright 2013-2015 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for sending emails from within a Lino application.

.. autosummary::
   :toctree:

   mixins
   choicelists
   fixtures.hello


"""

from lino import ad
from django.utils.translation import gettext_lazy as _


class Plugin(ad.Plugin):

    verbose_name = _("Outbox")

    needs_plugins = ['lino.modlib.uploads']

    MODULE_LABEL = _("Outbox")

    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('outbox.MyOutbox')

    def setup_explorer_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('outbox.Mails')
        m.add_action('outbox.Attachments')
