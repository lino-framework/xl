
"""tables for `lino_xl.lib.mailbox`.

"""
# import logging
#
# logger = logging.getLogger(__name__)



from django.utils.translation import ugettext_lazy as _

from lino.api import dd

class Mailboxes(dd.Table):
    model = "mailbox.Mailbox"
    insert_layout = """
        name
        uri
        from_email
        active
        """
    detail_layout = """
    name uri from_email"""

class Mail(dd.Table):
    model = "mailbox.Message"
