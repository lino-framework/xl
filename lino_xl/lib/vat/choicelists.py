# Copyright 2012-2015 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""
Choicelists for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, _


class VatClasses(dd.ChoiceList):
    """
    A VAT class is a direct or indirect property of a trade object
    (e.g. a Product) which determines the VAT *rate* to be used.  It
    does not contain the actual rate because this still varies
    depending on your country, the time and type of the operation, and
    possibly other factors.

    Default classes are:

    .. attribute:: exempt

    .. attribute:: reduced

    .. attribute:: normal


    """
    verbose_name = _("VAT Class")
    verbose_name_plural = _("VAT Classes")

add = VatClasses.add_item
add('0', _("Exempt"), 'exempt')    # post stamps, ...
add('1', _("Reduced"), 'reduced')  # food, books,...
add('2', _("Normal"), 'normal')    # everything else


class VatRegime(dd.Choice):
    "Base class for choices of :class:`VatRegimes`."

    item_vat = True
    "Whether unit prices are VAT included or not."


class VatRegimes(dd.ChoiceList):
    """
    The VAT regime is a classification of the way how VAT is being
    handled, e.g. whether and how it is to be paid.

    """
    verbose_name = _("VAT regime")
    verbose_name_plural = _("VAT regimes")
    item_class = VatRegime
    help_text = _(
        "Determines how the VAT is being handled, \
        i.e. whether and how it is to be paid.")

add = VatRegimes.add_item
add('10', _("Private person"), 'private')
add('11', _("Private person (reduced)"), 'reduced')
add('20', _("Subject to VAT"), 'subject')
add('25', _("Co-contractor"), 'cocontractor')
add('30', _("Intra-community"), 'intracom')
add('40', _("Outside EU"), 'outside')
add('50', _("Exempt"), 'exempt', item_vat=False)
add('70', _("Germany"), 'de')
add('71', _("Luxemburg"), 'lu')


