# -*- coding: UTF-8 -*-
# Copyright 2013-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Adds functionality for receiving emails and storing them in the db.

"""

from lino import ad
from django.utils.translation import ugettext_lazy as _
from unipath import Path

class Plugin(ad.Plugin):

    verbose_name = _("Mailbox")

    needs_plugins = ["django_mailbox"]

    mailbox_templates = []

    def add_mailbox(self, protocol, name, origin):
        origin = Path(origin).resolve()
        # print(origin.stat())
        if not origin.exists():
            raise Exception("No such file: {}".format(origin))
        self.mailbox_templates.append((protocol, name, origin))

    def setup_main_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.UnassignedMessages')

    def setup_config_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.Mailboxes')
        # m.add_action('mailbox.Mailboxes')

    def setup_explorer_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('mailbox.Messages')

    def get_requirements(self, site):
        try:
            import django_mailbox
            # leave unchanged if it is already installed
        except ImportError:
            # yield "django-mailbox"
            yield "git+https://github.com/khchine5/django-mailbox.git#egg=django-mailbox"

        # If the unpatched version is used, you get AttributeError: type
        # object 'Message' has no attribute 'collect_virtual_fields'.

    def get_used_libs(self, html=None):
        try:
            #~ import appy
            from django_mailbox import __version__ as version
        except ImportError:
            version = self.site.not_found_msg
        yield ("django_mailbox", version, "https://github.com/CylonOven/django-mailbox")


    #list of mboxes that are to be handeled.

    #reply_addr = "replys@localhost"
    # reply_addr = None  #
    # mbox_path = None
