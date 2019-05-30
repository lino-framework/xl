# -*- coding: utf-8 -*-
"""Class to parse camt files."""
##############################################################################
#
#    Copyright (C) 2013-2015 Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# File taken from https://github.com/OCA/bank-statement-import/blob/8.0/account_bank_statement_import_camt/camt.py

# Modifications by Luc Saffre:

# Replaced classes defined in parserlib by simple pythonic classes.
# The original completely ignored the ``<Dt>``
# element of opening and closing balances.  Their statement had a date
# which was the `execution_date` of the first transaction.  Now they
# set two dates `start_date` and `end_date`.
# The original ignored the sequence number (legal or electronic).
# balances not float but Decimal

# http://lxml.de/xpathxslt.html


import re
from datetime import datetime
from decimal import Decimal
from lxml import etree

from lino_xl.lib.ledger.utils import ZERO


class BankTransaction(object):
    """Single transaction that is part of a bank statement."""

    def __init__(self, stmt, seqno):
        """Define and initialize attributes.

        Not all attributes are already used in the actual import.
        """
        self.statement = stmt
        self.seqno = seqno
        self.value_date = None  # The value date of the action
        self.name = None  # unique id ?
        self.txcd = ''  # Action type that initiated this message
        self.txcd_issuer = ''
        self.booking_date = None  # The posted date of the action
        self.remote_account_iban = None  # The account of the other party
        self.remote_account_other = None  # The account of the other party
        self.remote_currency = None  # The currency used by the other party
        self.exchange_rate = None
        # The exchange rate used for conversion of local_currency and
        # remote_currency
        self.transferred_amount = None  # actual amount transferred
        self.message = None  # message from the remote party
        self.eref = None  # end to end reference for transactions
        self.remote_owner = None  # name of the other party
        self.remote_owner_address = ''  # other parties address lines
        self.remote_owner_city = None  # other parties city name
        self.remote_owner_postalcode = None  # other parties zip code
        self.remote_owner_country_code = None  # other parties country code
        self.remote_bank_bic = None  # bic of other party's bank
        self.provision_costs = None  # costs charged by bank for transaction
        self.provision_costs_currency = None
        self.provision_costs_description = None
        self.error_message = None  # error message for interaction with user
        self.storno_retry = None
        # If True, make cancelled debit eligible for a next direct debit run
        # self.data = ''  # Raw data from which the transaction has been parsed

    # @property
    # def unique_import_id(self):
    #     return self.statement.statement_id + str(self.seqno).zfill(4)


class BankStatement(object):
    """A bank statement groups data about several bank transactions."""

    def __init__(self):
        self.statement_id = None
        self.legal_sequence_number = None
        self.electronic_sequence_number = None
        self.local_account = None
        self.account_name = ''
        self.owner_name = ''
        self.local_currency = None
        self.start_date = None
        self.end_date = None
        self.start_balance = None
        self.end_balance = None
        self.transactions = []

    def create_transaction(self):
        """Create and append transaction.
        """
        obj = BankTransaction(self, len(self.transactions) + 1)
        self.transactions.append(obj)
        return obj

    @property
    def unique_id(self):
        year = self.end_date.year
        if False:
            # disabled 20170612 because this is allowed and even
            # normal for the first statement of every year.
            if self.start_date.year != year:
                raise Exception(
                    "%s starts %s and ends %s (different years)" % (
                        self, self.start_date, self.end_date))
        num = self.electronic_sequence_number
        if num is None:
            raise Exception(
                "%s has no electronic_sequence_number" % self)
        return str(year) + "/" + str(num).zfill(4)
        
    def __str__(self):
        return "Statement %s" % self.statement_id


class CamtParser(object):
    """Parser for camt bank statement import files."""

    def parse_date(self, ns, node):
        """"Parse a <Bal> element for a <Dt>."""
        dt = node.xpath('ns:Dt/ns:Dt', namespaces={'ns': ns})
        if dt:
            return datetime.strptime(dt[0].text, "%Y-%m-%d")
        
    def parse_amount(self, ns, node):
        """Parse element that contains Amount and CreditDebitIndicator."""
        if node is None:
            return ZERO
        sign = 1
        amount = ZERO
        sign_node = node.xpath('ns:CdtDbtInd', namespaces={'ns': ns})
        if sign_node and sign_node[0].text == 'DBIT':
            sign = -1
        amount_node = node.xpath('ns:Amt', namespaces={'ns': ns})
        if amount_node:
            amount = sign * Decimal(amount_node[0].text)
        return amount

    def add_value_from_node(
            self, ns, node, xpath_str, obj, attr_name, join_str=None):
        """Add value to object from first or all nodes found with xpath.

        If xpath_str is a list (or iterable), it will be seen as a series
        of search path's in order of preference. The first item that results
        in a found node will be used to set a value."""
        if not isinstance(xpath_str, (list, tuple)):
            xpath_str = [xpath_str]
        for search_str in xpath_str:
            found_node = node.xpath(search_str, namespaces={'ns': ns})
            if found_node:
                if join_str is None:
                    attr_value = found_node[0].text
                else:
                    attr_value = join_str.join([x.text for x in found_node])
                setattr(obj, attr_name, attr_value)
                break

    def parse_transaction_details(self, ns, node, transaction):
        """Parse transaction details (message, party, account...)."""
        # message
        self.add_value_from_node(
            ns, node, [
                './ns:RmtInf/ns:Ustrd',
                './ns:AddtlTxInf',
                './ns:AddtlNtryInf',
            ], transaction, 'message', join_str='\n')
        # eref
        self.add_value_from_node(
            ns, node, [
                './ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref',
                './ns:Refs/ns:EndToEndId',
            ],
            transaction, 'eref', join_str='\n'
        )
        # remote party values
        party_type = 'Dbtr'
        party_type_node = node.xpath(
            '../../ns:CdtDbtInd', namespaces={'ns': ns})
        if party_type_node and party_type_node[0].text != 'CRDT':
            party_type = 'Cdtr'
        party_node = node.xpath(
            './ns:RltdPties/ns:%s' % party_type, namespaces={'ns': ns})
        if party_node:
            self.add_value_from_node(
                ns, party_node[0], './ns:Nm', transaction, 'remote_owner')
            self.add_value_from_node(
                ns, party_node[0], './ns:PstlAdr/ns:Ctry', transaction,
                'remote_owner_country'
            )
            address_node = party_node[0].xpath(
                './ns:PstlAdr/ns:AdrLine', namespaces={'ns': ns})
            if address_node:
                transaction.remote_owner_address = '\n'.join(
                    [ln.text for ln in address_node])
        # Get remote_account from iban or from domestic account:
        account_node = node.xpath(
            './ns:RltdPties/ns:%sAcct/ns:Id' % party_type,
            namespaces={'ns': ns}
        )
        if account_node:
            iban_node = account_node[0].xpath(
                './ns:IBAN', namespaces={'ns': ns})
            if iban_node:
                transaction.remote_account_iban = iban_node[0].text
                bic_node = node.xpath(
                    './ns:RltdAgts/ns:%sAgt/ns:FinInstnId/ns:BIC' % party_type,
                    namespaces={'ns': ns}
                )
                if bic_node:
                    transaction.remote_bank_bic = bic_node[0].text
            else:
                self.add_value_from_node(
                    ns, account_node[0], './ns:Othr/ns:Id', transaction,
                    'remote_account_other'
                )

    def parse_transaction(self, ns, node, transaction):
        """Parse transaction (entry) node."""
        self.add_value_from_node(
            ns, node, './ns:BkTxCd/ns:Prtry/ns:Cd', transaction,
            'txcd'
        )
        self.add_value_from_node(
            ns, node, './ns:BkTxCd/ns:Prtry/ns:Issr', transaction,
            'txcd_issuer'
        )
        self.add_value_from_node(
            ns, node, './ns:BookgDt/ns:Dt', transaction, 'booking_date')
        self.add_value_from_node(
            ns, node, './ns:ValDt/ns:Dt', transaction, 'value_date')
        transaction.transferred_amount = self.parse_amount(ns, node)
        details_node = node.xpath(
            './ns:NtryDtls/ns:TxDtls', namespaces={'ns': ns})
        if details_node:
            self.parse_transaction_details(ns, details_node[0], transaction)
        #transaction.data = etree.tostring(node)
        return transaction

    def parse_balance_amounts(self, statement, ns, node):
        """Return opening and closing balance.

        Depending on kind of balance and statement, the balance might be in a
        different kind of node:
        OPBD = OpeningBalance
        PRCD = PreviousClosingBalance
        ITBD = InterimBalance (first ITBD is start-, second is end-balance)
        CLBD = ClosingBalance
        """
        start_balance_node = None
        end_balance_node = None
        for node_name in ['OPBD', 'PRCD', 'CLBD', 'ITBD']:
            code_expr = (
                './ns:Bal/ns:Tp/ns:CdOrPrtry/ns:Cd[text()="%s"]/../../..' %
                node_name
            )
            balance_node = node.xpath(code_expr, namespaces={'ns': ns})
            if balance_node:
                if node_name in ['OPBD', 'PRCD']:
                    start_balance_node = balance_node[0]
                elif node_name == 'CLBD':
                    end_balance_node = balance_node[0]
                else:
                    if not start_balance_node:
                        start_balance_node = balance_node[0]
                    if not end_balance_node:
                        end_balance_node = balance_node[-1]

        statement.start_date = self.parse_date(ns, start_balance_node)
        statement.start_balance = self.parse_amount(ns, start_balance_node)

        statement.end_balance = self.parse_amount(ns, end_balance_node)
        statement.end_date = self.parse_date(ns, end_balance_node)

    def parse_statement(self, ns, node):
        """Parse a single Stmt node."""
        statement = BankStatement()
        self.add_value_from_node(
            ns, node, [
                './ns:Acct/ns:Id/ns:IBAN',
                './ns:Acct/ns:Id/ns:Othr/ns:Id',
            ], statement, 'local_account'
        )
        self.add_value_from_node(
            ns, node, './ns:Id', statement, 'statement_id')
        self.add_value_from_node(
            ns, node, './ns:LglSeqNb', statement, 'legal_sequence_number')
        self.add_value_from_node(
            ns, node, './ns:ElctrncSeqNb', statement,
            'electronic_sequence_number')
        self.add_value_from_node(
            ns, node, './ns:Acct/ns:Ccy', statement, 'local_currency')

        self.add_value_from_node(
            ns, node, './ns:Acct/ns:Nm', statement, 'account_name')
        self.add_value_from_node(
            ns, node, './ns:Acct/ns:Ownr/ns:Nm', statement, 'owner_name')

        self.parse_balance_amounts(statement, ns, node)
        transaction_nodes = node.xpath('./ns:Ntry', namespaces={'ns': ns})
        for entry_node in transaction_nodes:
            transaction = statement.create_transaction()
            self.parse_transaction(ns, entry_node, transaction)
        return statement

    def check_version(self, ns, root):
        """Validate validity of camt file."""
        # Check wether it is camt at all:
        re_camt = re.compile(
            r'(^urn:iso:std:iso:20022:tech:xsd:camt.'
            r'|^ISO:camt.)'
        )
        if not re_camt.search(ns):
            raise ValueError('no camt: ' + ns)
        # Check wether version 052 or 053:
        re_camt_version = re.compile(
            r'(^urn:iso:std:iso:20022:tech:xsd:camt.053.'
            r'|^urn:iso:std:iso:20022:tech:xsd:camt.052.'
            r'|^ISO:camt.053.'
            r'|^ISO:camt.052.)'
        )
        if not re_camt_version.search(ns):
            raise ValueError('no camt 052 or 053: ' + ns)
        # Check GrpHdr element:
        root_0_0 = root[0][0].tag[len(ns) + 2:]  # strip namespace
        if root_0_0 != 'GrpHdr':
            raise ValueError('expected GrpHdr, got: ' + root_0_0)

    def parse(self, data):
        """Parse a camt.052 or camt.053 file."""
        try:
            root = etree.fromstring(
                data, parser=etree.XMLParser(recover=True))
        except etree.XMLSyntaxError:
            # ABNAmro is known to mix up encodings
            root = etree.fromstring(
                data.decode('iso-8859-15').encode('utf-8'))
        if root is None:
            raise IOError(
                'Not a valid xml file, or not an xml file at all.')
        ns = root.tag[1:root.tag.index("}")]
        self.check_version(ns, root)
        for node in root[0][1:]:
            statement = self.parse_statement(ns, node)
            if len(statement.transactions):
                yield statement
