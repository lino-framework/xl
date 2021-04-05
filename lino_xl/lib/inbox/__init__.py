# Copyright 2013-2016 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality for receiving and handing them inside a Lino application.

.. autosummary::
   :toctree:

"""

from lino import ad
from django.utils.translation import gettext_lazy as _


class Plugin(ad.Plugin):

    verbose_name = _("Inbox")

    needs_plugins = ['lino.modlib.comments']

    MODULE_LABEL = _("Inbox")


    #list of mboxes that are to be handeled.
    comment_reply_addr = "comments@site.com"
    mbox_path = None