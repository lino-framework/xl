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

    MODULE_LABEL = _("Mailbox")


    #list of mboxes that are to be handeled.

    #reply_addr = "replys@localhost"
    # reply_addr = None  #
    # mbox_path = None
