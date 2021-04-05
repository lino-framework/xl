# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino.utils.dates import AMONTH


def objects():
    REQUEST = settings.SITE.login()
    Journal = rt.models.ledger.Journal
    Company = rt.models.contacts.Company
    Declaration = rt.models.bevat.Declaration

    office = Company(
        name="Mehrwertsteuer-Kontrollamt Eupen",
        street="Vervierser Str. 8",
        country_id="BE", zip_code="4700")
    yield office

    USERS = Cycler(settings.SITE.user_model.objects.all())
    JOURNAL = Journal.objects.get(ref=rt.models.bevat.DEMO_JOURNAL_NAME)

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
