# -*- coding: UTF-8 -*-
# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


class Mailboxes(dd.Table):
    model = "django_mailbox.Mailbox"
    insert_layout = """
        name
        uri
        from_email
        active
        """
    detail_layout = """
    name uri from_email
    MessagesByMailbox
    """

class MessageDetail(dd.DetailLayout):
    main = "general preview"

    general = dd.Panel("""
    from_header subject ticket
    to_header
    MessageAttachmentsByMessage
    """, label=_("General"))

class Messages(dd.Table):
    model = "django_mailbox.Message"
    detail_layout = MessageDetail()
    # editable = False
    parameters = dict(
        show_assigned=dd.YesNo.field(_("Assigned"), blank=True))
        # not_assigned=dd.models.BooleanField(
        #     _("show only non assigned"),
        #     default=False))

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Messages, self).get_request_queryset(ar, **kwargs)
        pv = ar.param_values

        if pv.show_assigned == dd.YesNo.no:
            qs = qs.filter(ticket__isnull=True)
        elif pv.show_assigned == dd.YesNo.yes:
            qs = qs.filter(ticket__isnull=False)

        # if pv.not_assigned:
        #     qs = qs.filter(ticket__isnull=True)
        return qs

class MessagesByMailbox(Messages):
    master_key = "mailbox"

class UnassignedMessages(Messages):
    column_names = "processed subject from_header spam ticket *"
    # cell_edit = False

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(UnassignedMessages, self).param_defaults(ar, **kw)
        # kw.update(not_assigned=True)
        kw.update(show_assigned=dd.YesNo.no)
        return kw


class MessageAttachments(dd.Table):
    model = "django_mailbox.MessageAttachment"
    detail_layout = """document
                    headers """
    editable = False


class MessageAttachmentsByMessage(MessageAttachments):
    master_key = 'message'
    column_names = """headers document"""
