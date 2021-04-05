# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for receiving emails and storing them in the db.

This isn't being used anywhere (see :ticket:`4005`).  We stopped having it
tested because there are multiple problems. Last usage was in
:mod:`lino_book.projects.noi1e`.

We use a fork of the original django-mailbox package because we inject fields
into the models, which is possible only for real Lino models. (I tried to add
this field injecting magic also to plain Django models, by calling
:meth:`lino.core.model.Model.django2lino` already when the model is prepared
(see :mod:`lino.core.inject`), but that's not trivial and causes other issues.

The original `django-mailbox
<https://github.com/coddingtonbear/django-mailbox/issues/150>`__ causes the demo
fixture to fail with "eml: this field cannot be blank".

"""

from lino import ad
from django.utils.translation import gettext_lazy as _
from unipath import Path

class Plugin(ad.Plugin):

    verbose_name = _("Mailbox")

    # needs_plugins = ["django_mailbox"]  replaced by get_required_plugins

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

    def get_required_plugins(self):
        # for p in super(Plugin, self).get_required_plugins():
        #     yield p
        # add django_mailbox to INSTALLED_APPS only if it installed
        try:
            import django_mailbox
            yield "django_mailbox"
        except ImportError:
            pass

    def get_requirements(self, site):
        try:
            import django_mailbox
            # leave unchanged if it is already installed
        except ImportError:
            # yield "django_mailbox"
            yield "django-mailbox@git+https://github.com/tonispiip/django-mailbox"
            # yield "git+https://github.com/khchine5/django-mailbox.git#egg=django-mailbox"
            # if the unpatched version is used, you get
            # AttributeError: type object 'Message' has no attribute 'collect_virtual_fields'.
            # because you cannot inject fields into plain Django models

    def get_used_libs(self, html=None):
        try:
            #~ import appy
            from django_mailbox import __version__ as version
        except ImportError:
            version = self.site.not_found_msg
        yield ("django_mailbox", version, "https://github.com/TonisPiip/django-mailbox")


    #list of mboxes that are to be handled.

    #reply_addr = "replys@localhost"
    # reply_addr = None  #
    # mbox_path = None
