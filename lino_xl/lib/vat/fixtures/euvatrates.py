# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds VAT rules (:class:`lino_xl.lib.vat.VatRule`) for some
European countries.

"""

from lino.api import dd, rt


def objects():
    Country = rt.models.countries.Country
    # VatRule = rt.models.vat.VatRule
    vat = rt.models.vat

    def rule(vat_class, country_id, vat_regime, rate,
             trade_type=None, vat_account=None, vat_returnable_account=None):
        Account = rt.models.accounts.Account
        kw = dict()
        if country_id is None:
            country = None
        else:
            try:
                country = Country.objects.get(pk=country_id)
                kw.update(country=country)
            except Country.DoesNotExist:
                raise Exception("No country {0}".format(country_id))
        if trade_type:
            kw.update(trade_type=vat.TradeTypes.get_by_name(trade_type))
        if vat_account:
            kw.update(vat_account=Account.get_by_ref(vat_account))
        if vat_returnable_account:
            kw.update(vat_returnable_account=Account.get_by_ref(vat_returnable_account))
            
        return vat.VatRule(
            vat_class=vat.VatClasses.get_by_name(vat_class),
            vat_regime=vat.VatRegimes.get_by_name(vat_regime),
            rate=rate, **kw)

    yield rule('exempt', None, None, 0)

    from lino_xl.lib.ledger.accounts import (
        VAT_DUE_ACCOUNT, VAT_DEDUCTIBLE_ACCOUT, VAT_RETURNABLE_ACCOUNT)

    yield rule('normal', 'BE', None, '0.21', 'sales', VAT_DUE_ACCOUNT)
    yield rule('reduced', 'BE', None, '0.07', 'sales', VAT_DUE_ACCOUNT)
    yield rule(None, 'BE', 'intracom', '0.21',
               'purchases', VAT_DEDUCTIBLE_ACCOUT, VAT_RETURNABLE_ACCOUNT)
    yield rule('normal', 'BE', None, '0.21', 'purchases',
               VAT_DEDUCTIBLE_ACCOUT)
    yield rule('reduced', 'BE', None, '0.07', 'purchases',
               VAT_DEDUCTIBLE_ACCOUT)

    if False:

        yield rule('normal', 'EE', None, '0.20')
        yield rule('reduced', 'EE', None, '0.09')

        yield rule('normal', 'NL', None, '0.21')
        yield rule('reduced', 'NL', None, '0.06')

        yield rule('normal', 'DE', None, '0.19')
        yield rule('reduced', 'DE', None, '0.07')

        yield rule('normal', 'FR', None, '0.20')
        yield rule('reduced', 'FR', None, '0.10')
        # in FR there are more VAT classes, we currently don't support them
        # yield rule('reduced', 'FR', None, None, '0.055')
        # yield rule('reduced', 'FR', None, None, '0.021')

