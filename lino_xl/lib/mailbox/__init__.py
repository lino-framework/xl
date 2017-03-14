# Copyright 2013-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Adds functionality for receiving emails and storing them in the db.

.. autosummary::
   :toctree:

"""

from lino import ad
from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):

    verbose_name = _("Mailbox")

    needs_plugins = ["django_mailbox"]

    def setup_main_menu(self, site, profile, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.UnassignedMessages')

    def setup_config_menu(self, site, profile, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.Mailboxes')
        # m.add_action('mailbox.Mailboxes')

    def setup_explorer_menu(self, site, profile, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.Messages')



    #list of mboxes that are to be handeled.

    #reply_addr = "replys@localhost"
    # reply_addr = None  #
    # mbox_path = None
