# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds a single VAT rule (:mod:`lino_xl.lib.vat.models.VatRule`)
which applies 0% for all
:attr:`lino_xl.lib.vat.choicelists.VatClasses`.  To be used by
organizations without VAT number but using :mod:`lino_xl.lib.vat`.

"""

from lino.api import rt


def objects():

    yield rt.models.vat.VatRule(rate=0)
