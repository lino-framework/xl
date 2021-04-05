# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
The :term:`dummy module` for `outbox`, 
used by :func:`lino.core.utils.resolve_app`.
"""
from lino.api import dd


class Mailable(object):
    pass

#~ class MailableType(object): pass


class MailableType(dd.Model):
    email_template = dd.DummyField()
    attach_to_email = dd.DummyField()

    class Meta:
        abstract = True

MailsByController = dd.DummyField()
