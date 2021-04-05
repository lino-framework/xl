# Copyright 2012-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _

ledger = dd.resolve_app('ledger')


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
