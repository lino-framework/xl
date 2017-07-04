# Copyright 2012-2017 Luc Saffre


"""
Choicelists for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, _
from lino_xl.lib.ledger.roles import LedgerStaff


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
    required_roles = dd.login_required(LedgerStaff)

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
    required_roles = dd.login_required(LedgerStaff)
    help_text = _(
        "Determines how the VAT is being handled, \
        i.e. whether and how it is to be paid.")

add = VatRegimes.add_item
add('10', _("Private person"), 'private')
add('11', _("Private person (reduced)"), 'reduced')
add('20', _("Subject to VAT"), 'subject')
add('25', _("Co-contractor"), 'cocontractor')
add('30', _("Intra-community"), 'intracom')
add('31', _("Delay in collection"), 'delayed') # report de perception
add('40', _("Inside EU"), 'inside')
add('50', _("Outside EU"), 'outside')
add('60', _("Exempt"), 'exempt', item_vat=False)
add('70', _("Germany"), 'de')
add('71', _("Luxemburg"), 'lu')


