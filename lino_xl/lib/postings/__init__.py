# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Adds functionality for managing postings.

.. autosummary::
   :toctree:

    mixins
    dummy

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Postings")

    def setup_main_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('postings.MyPostings')
        m.add_action('postings.PostingsReady')
        m.add_action('postings.PostingsPrinted')
        m.add_action('postings.PostingsSent')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('postings.Postings')
