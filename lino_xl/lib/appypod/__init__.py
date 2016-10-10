# Copyright 2014-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""This plugin installs a series of build methods for generating
printable documents using LibreOffice.

These build methods require a running LibreOffice server (see
:ref:`admin.oood`).  Compared to the built-in methods
:class:`WeasyBuildMethod
<lino.modlib.weasyprint.choicelists.WeasyBuildMethod>` and the (now
deprecated) :class:`PisaBuildMethod
<lino.modlib.printing.choicelists.PisaBuildMethod>`, this has the
disadvantage of requiring more effort to get started, but it has
several advantages:

- Can be used to produce editable files (`.rtf` or `.odt`) from the
  same `.odt` template.
- Features like automatic hyphenation, sophisticated fonts and layouts
  are beyond the scope of pisa or weasyprint.
- Templates are `.odt` files (not `.html`), meaning that end-users
  dare to edit them more easily.

This plugin also adds a generic button to "print" *any* table into PDF
using LibreOffice.

If `contacts` is installed, it also installs a
:class:`PrintLabelsAction
<lino_xl.lib.appypod.mixins.PrintLabelsAction>`.

.. xfile:: appypod/Table.odt

    Template used to print a table in landscape orientation.

.. xfile:: appypod/Table-portrait.odt

    Template used to print a table in portrait orientation.

.. xfile:: appypod/Labels.odt

    Template used to print address labels.


Usage see also :ref:`lino.admin.appypod`.

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

