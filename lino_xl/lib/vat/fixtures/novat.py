# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds a single VAT rule (:mod:`lino_xl.lib.vat.VatRule`) which
applies 0% for all operations.  To be used by organizations without
VAT number but using :mod:`lino_xl.lib.vat`.

"""

from lino.api import rt

from lino_xl.lib.ledger.accounts import VAT_DUE_ACCOUNT

def objects():
    TradeTypes = rt.models.ledger.TradeTypes
    Account = rt.models.accounts.Account
    VatRule = rt.models.vat.VatRule
    VatRegimes = rt.models.vat.VatRegimes
    VatClasses = rt.models.vat.VatClasses
    
    yield VatRule(
        rate='0.21', trade_type=TradeTypes.purchases,
        vat_account=Account.get_by_ref(VAT_DUE_ACCOUNT),
        vat_regime=VatRegimes.intracom,
        vat_class=VatClasses.normal,
        vat_returnable=True)
    yield VatRule(
        rate='0.21', trade_type=TradeTypes.purchases,
        vat_account=Account.get_by_ref(VAT_DUE_ACCOUNT),
        vat_regime=VatRegimes.intracom_supp,
        vat_class=VatClasses.normal,
        vat_returnable=True)
    yield VatRule(vat_regime=VatRegimes.normal, rate=0)
    yield VatRule(vat_regime=VatRegimes.subject, rate=0)
