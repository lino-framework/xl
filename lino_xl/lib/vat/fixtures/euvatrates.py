# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds VAT rules (:class:`lino_xl.lib.vat.VatRule`) for some
European countries.

"""

from lino.api import dd, rt
from lino_xl.lib.ledger.accounts import (
    VAT_DUE_ACCOUNT, VAT_DEDUCTIBLE_ACCOUT, VAT_RETURNABLE_ACCOUNT)



def objects():
    Account = rt.models.accounts.Account
    # Country = rt.models.countries.Country
    # VatRule = rt.models.vat.VatRule
    vat = rt.models.vat

    def rule(vat_class, rate, vat_area=None, trade_type=None,
             vat_regime=None, 
             vat_account=None,
             vat_returnable_account=None):
        kw = dict()
        if trade_type:
            kw.update(trade_type=vat.TradeTypes.get_by_name(trade_type))
        if vat_regime:
            kw.update(vat_regime=vat.VatRegimes.get_by_name(vat_regime))
        if vat_class:
            kw.update(vat_class=vat.VatClasses.get_by_name(vat_class))
        if vat_account:
            kw.update(vat_account=Account.get_by_ref(vat_account))
        if vat_returnable_account:
            kw.update(
                vat_returnable_account=Account.get_by_ref(
                    vat_returnable_account))
            
        return vat.VatRule(vat_area=vat_area, rate=rate, **kw)

    country_code = dd.plugins.countries.country_code
    NAT = vat.VatAreas.national
    EU = vat.VatAreas.eu
    INT = vat.VatAreas.international
    if country_code == "BE":
        yield rule('normal', '0.21', NAT, 'sales', None, VAT_DUE_ACCOUNT)
        yield rule('reduced', '0.07', NAT, 'sales', None, VAT_DUE_ACCOUNT)
        
        yield rule('normal', '0.21', NAT, 'purchases',
                   None, VAT_DEDUCTIBLE_ACCOUT)
        yield rule('reduced', '0.07', NAT, 'purchases',
                   None, VAT_DEDUCTIBLE_ACCOUT)
        yield rule(
            'normal', '0.21', EU, 'purchases',
            'intracom', VAT_DEDUCTIBLE_ACCOUT, VAT_RETURNABLE_ACCOUNT)
        yield rule(
            'reduced', '0.07', EU, 'purchases',
            'intracom', VAT_DEDUCTIBLE_ACCOUT, VAT_RETURNABLE_ACCOUNT)
        yield rule(
            'normal', '0.21', EU, 'sales',
            'intracom', VAT_DUE_ACCOUNT, VAT_RETURNABLE_ACCOUNT)
        yield rule(
            'reduced', '0.07', EU, 'sales',
            'intracom', VAT_DUE_ACCOUNT, VAT_RETURNABLE_ACCOUNT)
        # yield rule(None, 0, INT, 'purchases', 'outside')

    # yield rule('exempt', 0)
    yield rule(None, 0)

    # if country_code == "EE":
    #     yield rule('normal', 'EE', None, '0.20')
    #     yield rule('reduced', 'EE', None, '0.09')

    # if country_code == "NL":
    #     yield rule('normal', 'NL', None, '0.21')
    #     yield rule('reduced', 'NL', None, '0.06')

    # if country_code == "DE":
    #     yield rule('normal', 'DE', None, '0.19')
    #     yield rule('reduced', 'DE', None, '0.07')

    # if country_code == "FR":
    #     yield rule('normal', 'FR', None, '0.20')
    #     yield rule('reduced', 'FR', None, '0.10')
    #     # in FR there are more VAT classes, we currently don't support them
    #     # yield rule('reduced', 'FR', None, None, '0.055')
    #     # yield rule('reduced', 'FR', None, None, '0.021')

