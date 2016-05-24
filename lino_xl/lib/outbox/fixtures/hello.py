# -*- coding: UTF-8 -*-
# Copyright 2008-2015 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.
"""Creates a welcome mail for all persons in the database.
"""


from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models

from lino.utils.instantiator import Instantiator
from lino.core.utils import resolve_model

from lino.api import rt


def objects():

    from lino_xl.lib.outbox.models import RecipientType
    Person = rt.modules.contacts.Person

    root = settings.SITE.user_model.objects.get(username='root')

    mail = Instantiator('outbox.Mail').build
    recipient_to = Instantiator(
        'outbox.Recipient', type=RecipientType.to).build

    for p in Person.objects.filter(email=''):
        try:
            p.first_name.encode('ascii')
            p.email = p.first_name.lower() + "@example.com"
            p.save()
        except UnicodeError:
            pass

    for person in Person.objects.exclude(email=''):
        m = mail(user=root, subject='Welcome %s!' % person.first_name)
        yield m
        yield recipient_to(mail=m, partner=person)
