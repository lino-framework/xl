
"""tables for `lino_xl.lib.mailbox`.

"""
# import logging
#
# logger = logging.getLogger(__name__)



from django.utils.translation import ugettext_lazy as _

from lino.api import dd

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

class Messages(dd.Table):
    model = "django_mailbox.Message"
    detail_layout = """from_header to_header subject spam
    preview
    PointersByMessage MessageAttachmentsByMessage"""
    editable = False
    parameters = dict(
        not_assigned=dd.models.BooleanField(
            _("show only non assigned"),
            default=False))

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Messages, self).get_request_queryset(ar)
        pv = ar.param_values

        if pv.not_assigned:
            qs = qs.filter(pointer=None)
        return qs

class MessagesByMailbox(Messages):
    master_key = "mailbox"

class UnassignedMessages(Messages):

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(UnassignedMessages, self).param_defaults(ar, **kw)
        kw.update(not_assigned=True)
        return kw

class MessagePointers(dd.Table):
    model = "mailbox.MessagePointer"
    insert_layout = """message
    ticket"""
    detail_layout = """preview"""
    pass

class MessagesByTicket(MessagePointers):
    master_key = 'ticket'

class PointersByMessage(MessagePointers):
    column_names = "ticket ticket__summary"
    master_key = 'message'


class MessageAttachments(dd.Table):
    model = "django_mailbox.MessageAttachment"
    detail_layout = """document
                    headers """
    editable = False


class MessageAttachmentsByMessage(MessageAttachments):
    master_key = 'message'
    column_names = """headers document"""
