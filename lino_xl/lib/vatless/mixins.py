# -*- coding: UTF-8 -*-
# Copyright 2015-2016 Luc Saffre
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
