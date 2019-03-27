# Copyright 2012-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

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
    main = "info values"
    
    info = dd.Panel("""
    start_period end_period entry_date accounting_period
    ledger.MovementsByVoucher
    """, label=_("Info"))
    
    values = dd.Panel("""
    partner user workflow_buttons
    c2 c2b c2c c3 c3b c4 c5
    F61 F62 FXX FYY F71
    # VouchersByDeclaration
    """, label=_("Values"))
    
    c2="""
    F00 
    F01 
    F02 
    F03 
    """
    c2b="""
    # F44 
    F45
    F46
    """
    c2c="""
    F47
    F48
    F49
    """
    c3 = """
    F81 
    F82 
    F83
    F84 
    """
    c3b = """
    F85 
    F86 
    F87 
    """

    c4 = """
    F54
    F55 
    F56
    """
    c5 = """
    F59
    F64
    """
    
    # fields="""
    # F00 F01 F02 F03 
    # F44 F45 F46 F47 F48 F49
    # F81 F82 F83
    # F84 F85 F86 F87 F88
    # """


class Declarations(dd.Table):
    model = 'eevat.Declaration'
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
    column_names = "number_with_year entry_date start_period end_period accounting_period FXX FYY F71 workflow_buttons *"

ledger.VoucherTypes.add_item_lazy(DeclarationsByJournal)


