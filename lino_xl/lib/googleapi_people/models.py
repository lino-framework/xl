# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function
# from builtins import str
# from builtins import object

import logging
from googleapiclient.errors import HttpError
# from lino_xl.lib.contacts.models import Partner as oldPartner
# from lino_xl.lib.contacts.models import *
# from lino.modlib.users.models import *
from lino_xl.lib.googleapi_people.utils import service

logger = logging.getLogger(__name__)

from lino.api import dd, rt, _


# contacts = dd.resolve_app('contacts')
# Person = contacts.Person


class GooglePeople(dd.Model):
    class Meta:
        abstract = True

    google_resourceName = dd.CharField(max_length=200, verbose_name=_('Google ResourceName'), blank=True)
    google_contactID = dd.CharField(max_length=200, verbose_name=_('Google Contact ID'), blank=True)

    def save(self, *args, **kw):
        if not self.google_resourceName and self.name:
            body = {'names': [{'displayName': self.name, "givenName": self.last_name, "familyName": self.first_name}]}
            if self.email:
                body['emailAddresses'] = [{'value': self.email, 'type': 'work'}]
            if dd.is_installed('phones'):
                body.update(
                    {'PhoneNumber': [{'value': self.phone, 'type': 'main'}, {'value': self.gsm, 'type': 'mobile'}]})
            try:
                results = service.people().createContact(body=body).execute()
                if results and results.get('resourceName', False):
                    self.google_resourceName = results.get('resourceName', False)
                    self.google_contactID = results.get('resourceName', False).split('/')[1]
            except HttpError as e:
                print(e.content)
        elif self.google_resourceName:
            try:
                contactToUpdate = service.people().get(resourceName=self.google_resourceName,
                                                       personFields='names,emailAddresses').execute()
                contactToUpdate['names'] = [
                    {'displayName': self.name, "givenName": self.last_name,
                     "familyName": self.first_name}]
                service.people().updateContact(resourceName=self.google_resourceName,
                                               updatePersonFields='names,emailAddresses',
                                               body=contactToUpdate).execute()
            except HttpError as e:
                print(e.content)
        res = super(GooglePeople, self).save(*args, **kw)
        return res
