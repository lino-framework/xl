# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Creates demo VAT declarations.

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


import datetime
from dateutil.relativedelta import relativedelta as delta
from importlib import import_module

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino_xl.lib.vat.mixins import myround

vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')

from lino_xl.lib.declarations.models import AMONTH

# from lino.core.requests import BaseRequest
REQUEST = settings.SITE.login()  # BaseRequest()


def objects():

    Journal = rt.models.ledger.Journal
    Declaration = rt.models.declarations.Declaration
    DeclarationFields = rt.models.declarations.DeclarationFields
    Account = rt.models.accounts.Account

    m = import_module(dd.plugins.declarations.country_module)

    yield m.demo_objects()
    
    USERS = Cycler(settings.SITE.user_model.objects.all())
    JOURNAL = Journal.objects.get(ref="VAT")

    date = datetime.date(dd.plugins.ledger.start_year, 1, 4)
    end_date = settings.SITE.demo_date(-30) 
    while date < end_date:
        dcl = Declaration(
            journal=JOURNAL,
            user=USERS.pop(),
            voucher_date=date,
            entry_date=date + delta(days=5))
        yield dcl
        dcl.register(REQUEST)
        dcl.save()

        date += AMONTH
