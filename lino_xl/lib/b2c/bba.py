# -*- coding: UTF-8 -*-
# Copyright 2015 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""BBA Bank Transaction Code designations.

This module is obsolete and has been replaced by
:mod:`lino_xl.lib.b2c.febelfin`

"""

from __future__ import unicode_literals


def lines2dict(s):
    d = dict()
    for ln in s.splitlines():
        ln = ln.strip()
        if ln:
            k, txt = ln.split(None, 1)
            d[k] = txt
    return d

# - 01 to 39 : domestic or local SEPA transactions
# - 41 to 79 : foreign/non-SEPA  transactions
# - 80 to 89 : other families

FAMILIES = lines2dict("""
01 Domestic or local SEPA credit transfers
03 Cheques
04 Cards
05 Direct debit
07 Domestic commercial paper
09 Counter transactions
11 Securities
13 Credits
30 Miscellaneous transactions
35 Closing (e.g. periodical payments of interest, costs, ...)
41 Foreign -- non-SEPA credit transfers
43 Foreign cheques
47 Foreign commercial paper
80 Fees and commissions charged separately""")

CATEGORIES = lines2dict("""
000 Net amount
001 Interest credited
002 Interest debited
003 Credit fee
004 Postage
005 Letterbox rent
006 Various costs and fees
007 Right of access to databank
008 Information costs
009 Travelling costs
010 Bailiff fee
011 VAT
012 Exchange fee
013 Payment fee
014 Collection charges
015 Correspondent fee
017 Study charges
018 Rent guarantee charges
019 Tax on physical delivery
020 Physical delivery charges
021 Charges for drawing a bank cheque
022 Priority charges
023 Execution fee
024 Growth premium
025 Individual exchange costs account
026 Handling charges
027 Charges for dishonoured B/Es
028 Fidelity premium
029 Protest charges including cancellation charges
030 Account Insurance
031 Foreign cheque charges
032 Drawing of a circular cheque
033 Foreign security charges
034 Reinvestment charges
035 Foreign documentary security charges
036 Refused cheque charges
037 File handling costs
039 Telecommunication
041 Credit card charges
042 Payment card charges
043 Insurance costs
045 File handling costs
047 Security prolongation charges
049 Tax stamps / stamp duty
050 Capital long term investment
051 Withholding tax on income Basic amount

052 (European) home country withholding tax
053 Drawing up of forms
055 Loan or credit capital write-off
057 Interest subsidy
058 Capital premium
059 Interest on arrears
061 Transaction tariffing
063 Rounding off differences
065 Interest subsidy message
066 Fixed credit advance – reimbursement
067 Fixed credit advance – prolongation
068 Entry countervalue
069 Long-term arbitrage contracts : Amount to be paid by the customer
070 Long-term arbitrage contracts : Amount to be paid by the bank
071 Fixed credit advance – availability
072 Third persons fees countervalue
073 Foreign ATMs charges
074 Correspondence costs
100 Gross amount
200 Total documentary credit cost
201 Cancellation commission
202 Notification commission
203 Confirmation commission
204 Modification commission
205 Documentary payment commission
206 Commission for conditional guarantees/Payment
207 Divergencies commission
208 Commitment commission postponed payment
209 Transfer commission
210 Availability commission
211 Credit opening fee Additional credit opening fee
212 Storage charges
213 Financing charges
214 Issue charges (flow-through)
400 Acceptance commission
401 Visa charges
402 Certification charges
403 Minimum discount charges
404 Discount charges
405 Guarantee commission
406 Collection charges
407 Article 45 charges
""")

CODES = dict()
for k in FAMILIES.keys():
    CODES[k] = dict()

for ln in """
01 01 Individual transfer order
01 02 Individual transfer order initiated by the bank
01 03 Standing order
01 05 Payment of wages, etc.
01 07 Collective transfer
01 13 Transfer from your account
01 17 Financial centralisation
01 37 Costs
01 39 Your issue circular cheque
01 40 Codes proper to each bank
01 48 Codes proper to each bank
01 49 Cancellation or correction
01 50 Transfer in your favour
01 51 Transfer in your favour - initiated by the bank
01 52 Payment in your favour
01 54 Unexecutable transfer order
01 60 Non-presented circular cheque
01 62 Unpaid postal order
01 64 Transfer to your account
01 66 Financial centralization
01 87 Reimbursement of costs
01 90-98 Codes proper to each bank
01 99 Cancellation or correction


03 01 Payment of your cheque
03 05 Payment of voucher
03 09 Unpaid voucher
03 11 Department store cheque
03 15 Your purchase bank cheque
03 17 Your certified cheque
03 37 Cheque-related costs
03 38 Provisionally unpaid
03 40-48 Codes proper to each bank
03 49 Cancellation or correction
03 52 First credit of cheques, vouchers, luncheon vouchers, postal orders, credit under usual reserve
03 58 Remittance of cheques, vouchers, etc. credit after collection
03 60 Reversal of voucher
03 62 Reversal of cheque

03 63 Second credit of unpaid cheque
03 66 Remittance of cheque by your branch-credit under usual reserve
03 87 Reimbursement of cheque-related costs

03 90-98 Codes proper to each bank
03 99 Cancellation or correction

04 01 Loading a GSM card
04 02 Payment by means of a payment card within the Eurozone
04 03 Settlement credit cards
04 04 Cash withdrawal from an ATM
04 05 Loading Proton
04 06 Payment with tank card
04 07 Payment by GSM
04 08 Payment by means of a payment card outside the Eurozone
04 37 Costs
04 40-48 Codes proper to each bank
04 49 Cancellation or correction

04 50 Credit after a payment at a terminal
04 51 Unloading Proton
04 52 Loading GSM cards
04 53 Cash deposit at an ATM
04 55 Income from payments by GSM
04 68 Credit after Proton payments
04 87 Reimbursement of costs
04 90-98 Codes proper to each bank
04 99 Cancellation or correction

05 01 Payment
05 03 Unpaid debt
05 05 Reimbursement
05 37 Costs
05 40-48 Codes proper to each institution
05 49 Cancellation or correction

05 50 Credit after collection
05 52 Credit under usual reserve
05 54 Reimbursement
05 56 Unexecutable reimbursement
05 58 Reversal
05 87 Reimbursement of costs
05 90-98 Codes proper to each bank
05 99 Cancellation or correction

07 01 Payment commercial paper
07 05 Commercial paper claimed back
07 06 Extension of maturity date
07 07 Unpaid commercial paper
07 08 Payment in advance
07 09 Agio on supplier's bill
07 37 Costs related to commercial paper
07 39 Return of an irregular bill of exchange
07 40-48 Codes proper to each bank
07 49 Cancellation or correction

07 50 Remittance of commercial paper-credit after collection
07 52 Remittance of commercial paper-credit under usual reserve
07 54 Remittance of commercial paper for discount
07 56 Remittance of supplier's bill with guarantee
07 58 Remittance of supplier's bill without guarantee
07 87 Reimbursement of costs
07 90-98 Codes proper to each bank
07 99 Cancellation or correction


09 01 Cash withdrawal
09 05 Purchase of foreign bank notes
09 07 Purchase of gold/pieces
09 09 Purchase of petrol coupons
09 13 Cash withdrawal by your branch or agents
09 17 Purchase of fiscal stamps
09 19 Difference in payment
09 25 Purchase of traveller's cheque
09 37 Costs
09 40-48 Codes proper to each bank
09 49 Cancellation or correction

09 50 Cash payment
09 52 Payment night safe
09 58 Payment by your branch/agents
09 60 Sale of foreign bank notes
09 62 Sale of gold/pieces under usual reserve
09 68 Difference in payment
09 70 Sale of traveller's cheque
09 87 Reimbursement of costs
09 90-98 Codes proper to each bank
09 99 Cancellation or correction

11 01 Purchase of securities
11 02 Tenders
11 03 Subscription to securities
11 04 Issues
11 05 Partial payment subscription
11 06 Share option plan -- exercising an option
11 09 Settlement of securities
11 11 Payable coupons/repayable securities
11 13 Your repurchase of issue
11 15 Interim interest on subscription
11 17 Management fee
11 19 Regularisation costs
11 37 Costs
11 40-48 Codes proper to each bank
11 49 Cancellation or correction
11 50 Sale of securities
11 51 Tender
11 52 Payment of coupons from a deposit or settlement of coupons delivered over the counter - credit under usual reserve
11 58 Repayable securities from a deposit or delivered at the counter - credit under usual reserve
11 62 Interim interest on subscription When reimbursed separately to the subscriber
11 64 Your issue
11 66 Retrocession of issue commission
11 68 Compensation for missing coupon
11 70 Settlement of securities
11 87 Reimbursement of costs
11 90-98 Codes proper to each bank
11 99 Cancellation or correction

13 01 Short-term loan
13 02 Long-term loan
13 05 Settlement of fixed advance
13 07 Your repayment instalment credits
13 11 Your repayment mortgage loan
13 13 Settlement of bank acceptances
13 15 Your repayment hire-purchase and similar claims
13 19 Documentary import credits
13 21 Other credit applications
13 37 Credit-related costs
13 40-48 Codes proper to each bank
13 49 Cancellation or correction

13 50 Settlement of instalment credit
13 54 Fixed advance -- capital and interest
13 55 Fixed advance -- interest only
13 56 Subsidy
13 60 Settlement of mortgage loan
13 62 Term loan
13 68 Documentary export credits
13 70 Settlement of discount bank acceptance
13 87 Reimbursement of costs
13 90-98 Codes proper to each bank
13 99 Cancellation or correction

30 01 Spot purchase of foreign exchange
30 03 Forward purchase of foreign exchange
30 05 Capital and/or interest term investment
30 33 Value (date) correction
30 37 Costs
30 39 Undefined transaction
30 40-48 Codes proper to each bank
30 49 Cancellation or correction

30 50 Spot sale of foreign exchange
30 52 Forward sale of foreign exchange
30 54 Capital and/or interest term investment
30 55 Interest term investment
30 83 Value (date) correction
30 87 Reimbursement of costs
30 89 Undefined transaction
30 90-98 Codes proper to each bank
30 99 Cancellation or correction

35 01 Closing
35 37 Costs
35 40-48 Codes proper to each bank
35 49 Cancellation or correction

35 50 Closing
35 87 Reimbursement of costs
35 90-98 Codes proper to each bank
35 99 Cancellation or correction


41 01 Transfer
41 03 Standing order
41 05 Collective payments of wages
41 07 Collective transfers
41 13 Transfer from your account
41 17 Financial centralisation (debit)
41 37 Costs relating to outgoing foreign transfers and non-SEPA transfers
41 38 Costs relating to incoming foreign and non-SEPA transfers
41 40-48 Codes proper to each bank
41 49 Cancellation or correction

41 50 Transfer
41 64 Transfer to your account
41 66 Financial centralisation (credit)
41 87 Reimbursement of costs
41 90-98 Codes proper to each bank
41 99 Cancellation or correction

43 01 Payment of a foreign cheque
43 07 Unpaid foreign cheque
43 15 Purchase of an international bank cheque
43 37 Costs relating to payment of foreign cheques
43 40-48 Codes proper to each bank
43 49 Cancellation or correction

43 52 Remittance of foreign cheque credit under usual reserve
43 58 Remittance of foreign cheque credit after collection
43 62 Reversal of cheques
43 87 Reimbursement of costs
43 90-98 Codes proper to each bank
43 99 Cancellation or correction

47 01 Payment of foreign bill
47 05 Bill claimed back
47 06 Extension
47 07 Unpaid foreign bill
47 11 Payment documents abroad
47 13 Discount foreign supplier's bills
47 14 Warrant fallen due
47 37 Costs relating to the payment of a foreign bill
47 40-48 Codes proper to each bank
47 49 Cancellation or correction

47 50 Remittance of foreign bill credit after collection
47 52 Remittance of foreign bill credit under usual reserve
47 54 Discount abroad
47 56 Remittance of guaranteed foreign supplier's bill
47 58 Idem without guarantee
47 60 Remittance of documents abroad - credit under usual reserve
47 62 Remittance of documents abroad - credit after collection
47 64 Warrant
47 87 Reimbursement of costs
47 90-98 Codes proper to each bank
47 99 Cancellation or correction

80 02 Costs relating to electronic output
80 04 Costs for holding a documentary cash credit
80 06 Damage relating to bills and cheques
80 07 Insurance costs
80 08 Registering compensation for savings accounts
80 09 Postage
80 10 Purchase of Smartcard
80 11 Fees and commissions charged separately
80 12 Costs for opening a bank guarantee
80 13 Renting of safes
80 14 Handling costs instalment credit
80 15 Night safe
80 16 Bank confirmation to revisor or accountant
80 17 Charge for safe custody
80 18 Trade information
80 19 Special charge for safe custody
80 20 Drawing up a certificate
80 21 Pay-packet charges

80 22 Management/custody
80 23 Research costs
80 24 Participation in and management of interest refund system
80 25 Renting of direct debit box
80 26 Travel insurance premium
80 27 Subscription fee
80 29 Information charges
80 31 Writ service fee
80 33 Miscellaneous fees and commissions
80 35 Costs
80 37 Access right to database
80 39 Surety fee
80 41 Research costs
80 43 Printing of forms
80 45 Documentary credit charges
80 47 Charging fees for transactions
80 49 Cancellation or correction
80 99 Cancellation or correction
""".splitlines():
    ln = ln.strip()
    if ln:
        fam, cod, txt = ln.split(None, 2)
        CODES[fam][cod] = txt
        # print fam, cod
        # print u"""    '{0}{1}' : _("{2}"),""".format(fam, cod, txt)


def code2desc(c):
    """Return the description of the given code."""
    fam, cod = c[0:2], c[2:4]
    # return "{0} / {1} / {2}".format(
    #     FAMILIES[fam], CODES[fam][cod], CATEGORIES[cat])
    try:
        return CODES[fam][cod]
    except KeyError:
        return c
