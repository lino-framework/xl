# Copyright 2012-2017 Luc Saffre
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
    main = "info values"
    
    info = dd.Panel("""
    entry_date declared_period accounting_period
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
    F44 
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
    F88
    """

    c4 = """
    F54
    F55 
    F56
    F57
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
    model = 'bevat.Declaration'
    detail_layout = DeclarationDetail()
    insert_layout = """
    declared_period
    entry_date accounting_period
    """
    column_names = 'number declared_period accounting_period workflow_buttons *'
    # detail_layout = dd.DetailLayout("""
    # start_date end_date entry_date accounting_period user workflow_buttons
    # fields
    # VouchersByDeclaration
    # """, fields=DeclarationFields.fields_layout)


class DeclarationsByJournal(ledger.ByJournal, Declarations):
    params_panel_hidden = True
    #master = journals.Journal
    column_names = "number declared_period accounting_period user *"

from .models import Declaration
ledger.VoucherTypes.add_item(Declaration, DeclarationsByJournal)


