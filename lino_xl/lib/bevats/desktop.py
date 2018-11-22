# Copyright 2012-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Desktop UI for this plugin.

"""

from __future__ import unicode_literals

from lino.api import dd, _

ledger = dd.resolve_app('ledger')

#from .choicelists import DeclarationFields

from lino_xl.lib.vat.mixins import DECLARED_IN

if DECLARED_IN:
    
    class VouchersByDeclaration(ledger.Vouchers):
        column_names = 'overview entry_date accounting_period user *'
        master_key = 'declared_in'
        order_by = ['entry_date']
        editable = False
# else:        

#     class VouchersByDeclaration(dd.Table):
#         abstract = True
#         required_roles = set([1])

class DeclarationDetail(dd.DetailLayout):
    main = """
    start_period end_period entry_date accounting_period user
    partner narration workflow_buttons
    c1:10 c2:10 c2b:10 c3:10 c4:10
    ledger.MovementsByVoucher
    """
   
    c1 = """
    F71
    F72
    F73
    """
    
    c2 = """
    F75
    F76
    """
    c2b = """
    F77
    F78
    """
    c3 = """
    F80
    F81 
    F82
    """
    c4 = """
    F83
    printed
    """

    


class Declarations(dd.Table):
    model = 'bevats.Declaration'
    detail_layout = DeclarationDetail()
    insert_layout = """
    entry_date 
    start_period 
    end_period
    """
    column_names = 'number_with_year entry_date start_period end_period accounting_period user *'
    # detail_layout = dd.DetailLayout("""
    # start_date end_date entry_date accounting_period user workflow_buttons
    # fields
    # VouchersByDeclaration
    # """, fields=DeclarationFields.fields_layout)


class DeclarationsByJournal(ledger.ByJournal, Declarations):
    params_panel_hidden = True
    #master = journals.Journal
    column_names = "number_with_year entry_date start_period end_period accounting_period F80 F81 F82 F83 workflow_buttons *"

ledger.VoucherTypes.add_item_lazy(DeclarationsByJournal)


