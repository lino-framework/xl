# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Configures the vat_column of common accounts.

"""

from __future__ import unicode_literals

from lino_xl.lib.vat.choicelists import VatColumns
from lino_xl.lib.ledger.choicelists import CommonAccounts


def unused_objects():
    
    def dcl(ca, fld):
        obj = ca.get_object()
        if obj is None:
            return
        obj.vat_column = VatColumns.get_by_value(fld)
        return obj

    yield dcl(CommonAccounts.sales, '03')
    yield dcl(CommonAccounts.vat_due, '54')
    yield dcl(CommonAccounts.vat_deductible, '59')
    yield dcl(CommonAccounts.vat_returnable, '55')
    yield dcl(CommonAccounts.purchase_of_goods, '81')
    yield dcl(CommonAccounts.purchase_of_services, '82')
    yield dcl(CommonAccounts.purchase_of_investments, '83')


