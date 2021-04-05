# Copyright 2012-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _

ledger = dd.resolve_app('ledger')


class DeclarationDetail(dd.DetailLayout):
    main = "info values vat.MovementsByDeclaration"

    info = dd.Panel("""
    start_period end_period entry_date accounting_period
    ledger.MovementsByVoucher
    """, label=_("Info"))

    values = dd.Panel("""
    partner user workflow_buttons
    c1 c5 c2 c3 c4
    # VouchersByDeclaration
    # vat.SalesByDeclaration vat.PurchasesByDeclaration
    vat.SalesByDeclaration vat.PurchasesByDeclaration
    """, label=_("Values"))

    c1 = """
    F1a
    F1b
    F1
    F2a
    F2b
    F2
    """

    c5 = """
    F3
    F31
    F311
    F32
    F321
    """

    c2 = """
    F4
    F41
    F5
    F51
    F52
    F53
    F54
    """
    c3 = """
    F6
    F61
    F7
    F71
    """

    c4 = """
    F8
    F9
    F10
    F11
    F13
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
    column_names = "number_with_year entry_date start_period end_period accounting_period F1 F3 F4 F5 F13 workflow_buttons *"

ledger.VoucherTypes.add_item_lazy(DeclarationsByJournal)
