
"""Database models for `lino_xl.lib.mailbox`.

"""
import logging

logger = logging.getLogger(__name__)

from django_mailbox import models
from django.utils.translation import ugettext_lazy as _
import django.db.models
#
from lino.api import dd
#
#
#

def preview(obj, ar):
    return obj.html or obj.text

dd.inject_field('django_mailbox.Message', 'preview',
                dd.VirtualField(dd.HtmlBox(_("Preview")), preview))

class MessagePointer(dd.Model):

    class Meta:
        app_label ='mailbox'
        verbose_name =_("Message pointer")
        verbose_name_plural =_("Message pointers")

    @dd.htmlbox(_("Preview"))
    def preview(self, ar):
        if ar is None:
            return ""
        return self.message.html or self.message.text

    message = dd.ForeignKey("django_mailbox.Message", related_name="pointer")

    ticket = dd.ForeignKey('tickets.Ticket')



from .ui import *