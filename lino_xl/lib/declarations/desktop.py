# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Desktop UI for this plugin.

"""

from __future__ import unicode_literals

from lino.api import dd

ledger = dd.resolve_app('ledger')

from .models import Declaration
#from .choicelists import DeclarationFields

class VouchersByDeclaration(ledger.Vouchers):
    column_names = 'overview entry_date accounting_period user *'
    master_key = 'declared_in'
    order_by = ['entry_date']
    editable = False


class Declarations(dd.Table):
    model = 'declarations.Declaration'
    insert_layout = """
    start_date end_date
    entry_date accounting_period
    """
    column_names = 'number accounting_period start_date end_date workflow_buttons *'
    # detail_layout = dd.DetailLayout("""
    # start_date end_date entry_date accounting_period user workflow_buttons
    # fields
    # VouchersByDeclaration
    # """, fields=DeclarationFields.fields_layout)


class DeclarationsByJournal(ledger.ByJournal, Declarations):
    params_panel_hidden = True
    #master = journals.Journal
    column_names = "number accounting_period start_date end_date user *"

ledger.VoucherTypes.add_item(Declaration, DeclarationsByJournal)
