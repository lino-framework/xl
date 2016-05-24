# Copyright 2014-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

"""This plugin installs a series of build methods for generating
printable documents using LibreOffice.

These build methods require a running LibreOffice server (see
:ref:`admin.oood`).  Compared to the built-in :class:`PisaBuildMethod
<lino.modlib.printing.choicelists.PisaBuildMethod>`.  This has the
disadvantage of requiring more effort to get started, but it has
several advantages:

- Can be used to produce editable files (`.rtf` or `.odt`) from the
  same `.odt` template.
- Features like automatic hyphenation, sophisticated fonts and layouts
  are beyond the scope of pisa.
- Templates are `.odt` files (not `.html`), meaning that end-users
  dare to edit them more easily.

This plugin also adds a generic button to "print" *any* table into PDF
using LibreOffice.

.. autosummary::
   :toctree:

    choicelists
    mixins
    models

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."
    verbose_name = _("Appy POD")

