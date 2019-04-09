# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

import datetime

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino.utils.dates import AMONTH


def objects():
    REQUEST = settings.SITE.login()
    Journal = rt.models.ledger.Journal
    Company = rt.models.contacts.Company
    Declaration = rt.models.eevat.Declaration

    office = Company(
        name="Maksu- ja Tolliamet",
        street="Lõõtsa 8a",
        country_id="EE", zip_code="15176", city="Tallinn")
    yield office
    
    USERS = Cycler(settings.SITE.user_model.objects.all())
    JOURNAL = Journal.objects.get(ref=rt.models.eevat.DEMO_JOURNAL_NAME)

    date = datetime.date(dd.plugins.ledger.start_year, 1, 4)
    end_date = settings.SITE.demo_date(-30) 
    while date < end_date:
        dcl = Declaration(
            journal=JOURNAL,
            user=USERS.pop(),
            partner=office,
            entry_date=date,
            voucher_date=date)
        yield dcl
        dcl.register(REQUEST)
        dcl.save()

        date += AMONTH
