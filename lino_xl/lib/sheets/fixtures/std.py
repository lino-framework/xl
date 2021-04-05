# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Loads default sheet items.
Sets the :attr:`sheet_item` of common accounts.

"""

from lino_xl.lib.sheets.choicelists import CommonItems
from lino_xl.lib.ledger.choicelists import CommonAccounts


def objects():

    for i in CommonItems.get_list_items():
        yield i.create_object()

    def set_sheet_item(ca, ci):
        obj = CommonAccounts.get_by_name(ca).get_object()
        obj.sheet_item = CommonItems.get_by_name(ci).get_object()
        return obj

    yield set_sheet_item('customers', 'customers')
    yield set_sheet_item('pending_po', 'transfers')
    yield set_sheet_item('suppliers', 'suppliers')
    yield set_sheet_item('tax_offices', 'taxes')
    yield set_sheet_item('vat_due', 'taxes')
    yield set_sheet_item('vat_returnable', 'taxes')
    yield set_sheet_item('vat_deductible', 'taxes')
    yield set_sheet_item('due_taxes', 'taxes')
    yield set_sheet_item('waiting', 'transfers')
    yield set_sheet_item('best_bank', 'banks')
    yield set_sheet_item('cash', 'banks')
    yield set_sheet_item('purchase_of_goods', 'costofsales')
    yield set_sheet_item('purchase_of_services', 'operating')
    yield set_sheet_item('purchase_of_investments', 'otherexpenses')
    yield set_sheet_item('wages', 'operating')
    yield set_sheet_item('sales', 'sales')
    yield set_sheet_item('net_income', 'net_income')
    yield set_sheet_item('net_loss', 'net_loss')
    yield set_sheet_item('net_income_loss', 'net_income_loss')



