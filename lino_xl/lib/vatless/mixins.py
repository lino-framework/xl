# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


"""Model mixins for `lino_xl.lib.vatless`.


"""


from lino.api import dd


class PartnerDetailMixin(dd.DetailLayout):
    """Defines a panel :attr:`ledger`, to be added as a tab panel to your
    layout's `main` element.

    .. attribute:: ledger

        Shows the tables `vatless.VouchersByPartner` and
        `ledger.MovementsByPartner`.

    """
    if dd.is_installed('ledger'):
        ledger = dd.Panel("""
        payment_term
        vatless.VouchersByPartner
        ledger.MovementsByPartner
        """, label=dd.plugins.ledger.verbose_name)
    else:
        ledger = dd.DummyPanel()
