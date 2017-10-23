# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
# from builtins import str
# from builtins import object

import logging

# from lino_xl.lib.contacts.models import Partner as oldPartner
from lino_xl.lib.contacts.models import *
from lino_xl.lib.googleapi_people.utils import service

logger = logging.getLogger(__name__)

from lino.api import dd, rt, _


class GooglePeaple(dd.Model):
    class Meta:
        abstract = True

    google_resourceName = dd.CharField(max_length=200, verbose_name=_('Google ResourceName'))
    google_contactID = dd.CharField(max_length=200, verbose_name=_('Google Contact ID'))

    def on_create(self, ar):
        if not self.google_resourceName:
            body = {'names': [{'displayName': self.name}]}
            if dd.is_installed('phones'):
                body.update(
                    {'PhoneNumber': [{'value': self.phone, 'type': 'main'}, {'value': self.gsm, 'type': 'mobile'}]})
            results = service.people().createContact(body=body).execute()
            if results and results.get('resourceName', False):
                self.google_resourceName = results.get('resourceName', False)
        res = super(GooglePeaple, self).on_create(ar)
        return res


class Partner(Partner, GooglePeaple):

    class Meta(Partner.Meta):
        abstract = dd.is_abstract_model(__name__, 'Partner')
