# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models

try:
    import django_mailbox
except ImportError:
    django_mailbox = None

from lino.api import dd, rt, _


def preview(obj, ar):
    return obj.html or obj.text

def spam(obj):
    """Checks if the message is spam or not
    """
    if obj.subject.startswith("*****SPAM*****"):
        return True
    else:
        return False

if django_mailbox is not None:
    # When django_mailbox is not installed, this plugin does nothing, but it
    # must be importable for :manage:`install`.

    dd.inject_field('django_mailbox.Message', 'preview',
                    dd.VirtualField(dd.HtmlBox(_("Preview")), preview))
    dd.inject_field('django_mailbox.Message', 'ticket',
                    dd.ForeignKey('tickets.Ticket', blank=True, null=True))
    # dd.inject_field('django_mailbox.Message', 'spam',
    #                 models.BooleanField(_("Spam"), default=False))
    #
    dd.update_field('django_mailbox.Message', 'from_header', format="plain")

    @dd.schedule_often(10)
    def get_new_mail():
        for mb in rt.models.django_mailbox.Mailbox.objects.filter(active=True):
            # print("20210305", mb)
            mails = mb.get_new_mail()
            for mail in mails:
                if spam(mail):
                    mail.spam = True
                    mail.full_clean()
                    mail.save()
            if mails:
                dd.logger.info("got {} from mailbox: {}".format(mails, mb))


    class DeleteSpam(dd.Action):

        show_in_bbar = True
        readonly = False
        # required_roles = dd.login_required(Worker)
        label = "X"

        def run_from_ui(self, ar, **kw):
            spams = rt.models.django_mailbox.Message.objects.filter(spam=True)
            dd.logger.info("Deleting spam messages [%s]", spams)

            def ok(ar):
                for obj in spams:
                    obj.delete()
                ar.set_response(refresh=True)

            ar.confirm(
                ok,
                _("Delete {} messages.").format(spams.count()),
                _("Are you sure?"))

    dd.inject_action("django_mailbox.Message", delete_spam=DeleteSpam())

    from .ui import *
