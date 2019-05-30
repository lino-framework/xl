# -*- coding: UTF-8 -*-
# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)



from __future__ import unicode_literals

from lino.api import dd, _
from lino_xl.lib.sepa.roles import SepaUser


class Accounts(dd.Table):
    required_roles = dd.login_required(SepaUser)
    model = 'b2c.Account'
    detail_layout = """
    iban bic last_transaction owner_name account_name partners
    b2c.StatementsByAccount
    """
    column_names = "iban bic last_transaction partners owner_name account_name *"
    editable = False


class StatementDetail(dd.DetailLayout):
    main = """
    top_left top_right
    b2c.TransactionsByStatement
    """

    top_left = """
    account account__owner_name
    account__account_name statement_number local_currency
    """

    top_right = """
    balance_start start_date
    balance_end end_date
    """


class Statements(dd.Table):
    required_roles = dd.login_required(SepaUser)
    model = 'b2c.Statement'
    column_names = ('account statement_number '
                    'balance_start start_date balance_end end_date '
                    'local_currency *')
    order_by = ["-start_date"]
    detail_layout = StatementDetail()
    auto_fit_column_widths = True
    editable = False

    # insert_layout = dd.InsertLayout("""
    # account date
    # statement_number
    # balance_start balance_end
    # """, window_size=(60, 'auto'))


class StatementsByAccount(Statements):
    required_roles = dd.login_required(SepaUser)
    master_key = 'account'
    column_names = 'statement_number balance_start start_date balance_end end_date local_currency *'
    auto_fit_column_widths = True
    

class TransactionDetail(dd.DetailLayout):
    main = """
    statement seqno booking_date value_date amount
    remote_account remote_bic eref txcd_text
    remote_owner
    addr_left addr_right
    message
    """
    addr_left = "remote_owner_address"
    addr_right = """
    remote_owner_city
    remote_owner_postalcode
    remote_owner_country_code
    """


class Transactions(dd.Table):
    required_roles = dd.login_required(SepaUser)
    model = 'b2c.Transaction'
    editable = False
    detail_layout = TransactionDetail()
    column_names = "statement seqno value_date amount remote_account remote_owner *"


class TransactionsByStatement(Transactions):
    required_roles = dd.login_required(SepaUser)
    master_key = 'statement'
    column_names = 'booking_date amount remote_html message_html *'
    auto_fit_column_widths = True


