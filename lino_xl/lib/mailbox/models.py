
"""Database models for `lino_xl.lib.mailbox`.

"""
import logging

logger = logging.getLogger(__name__)

from django_mailbox import models
from django.utils.translation import ugettext_lazy as _
from lino.core.fields import ForeignKey

from lino.api import dd



class Mailbox(models.Mailbox,dd.Model):

    class Meta:
        app_label = 'mailbox'

        proxy = True
        auto_created = True
    pass

class Message(models.Message,dd.Model):

    class Meta:
        app_label = 'mailbox'

        proxy = True
        auto_created = True



from .ui import *