# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Creates demo VAT declarations.

"""

from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta as delta
# from importlib import import_module

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino_xl.lib.vat.choicelists import VatColumns
from lino.utils.dates import AMONTH
from lino_xl.lib.ledger.accounts import *



# from lino.core.requests import BaseRequest
REQUEST = settings.SITE.login()  # BaseRequest()

def demo_objects():
    
    def dcl(acc, fld):
        obj = rt.models.accounts.Account.get_by_ref(acc)
        obj.vat_column = VatColumns.get_by_value(fld)
        return obj

    yield dcl(SALES_ACCOUNT, '03')
    yield dcl(VAT_DUE_ACCOUNT, '54')
    yield dcl(VAT_DEDUCTIBLE_ACCOUT, '59')
    yield dcl(VAT_RETURNABLE_ACCOUNT, '55')
    # yield dcl(VATDCL_ACCOUNT, '20')
    yield dcl(PURCHASE_OF_GOODS, '81')
    yield dcl(PURCHASE_OF_SERVICES, '82')
    yield dcl(PURCHASE_OF_INVESTMENTS, '83')




def objects():

    Journal = rt.models.ledger.Journal
    Company = rt.models.contacts.Company
    Declaration = rt.models.bevat.Declaration
    # DeclarationFields = rt.models.declarations.DeclarationFields
    # Account = rt.models.accounts.Account

    # m = import_module(dd.plugins.declarations.country_module)
    # from lino_xl.lib.declarations.be import demo_objects

    yield demo_objects()

    agency = Company(name="Tax agency")
    yield agency
    
    USERS = Cycler(settings.SITE.user_model.objects.all())
    JOURNAL = Journal.objects.get(ref="VAT")

    date = datetime.date(dd.plugins.ledger.start_year, 1, 4)
    end_date = settings.SITE.demo_date(-30) 
    while date < end_date:
        dcl = Declaration(
            journal=JOURNAL,
            user=USERS.pop(),
            partner=agency,
            voucher_date=date,
            entry_date=date + delta(days=5))
        yield dcl
        dcl.register(REQUEST)
        dcl.save()

        date += AMONTH
