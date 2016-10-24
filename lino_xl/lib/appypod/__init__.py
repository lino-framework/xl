# Copyright 2014-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""This plugin adds a series of build methods for generating printable
documents using LibreOffice.

It also adds a generic button to "print" *any* table into PDF using
LibreOffice.  If :mod:`lino_xl.lib.contacts` (or a child thereof) is
installed, it adds a :class:`PrintLabelsAction
<lino_xl.lib.appypod.mixins.PrintLabelsAction>`.

Using these build methods requires a running LibreOffice server (see
:ref:`admin.oood`).  Compared to the built-in methods
:class:`WeasyBuildMethod
<lino.modlib.weasyprint.choicelists.WeasyBuildMethod>` and the (now
deprecated) :class:`PisaBuildMethod
<lino.modlib.printing.choicelists.PisaBuildMethod>`, this has several
advantages:

- Can be used to produce editable files (`.rtf` or `.odt`) from the
  same `.odt` template.
- Features like automatic hyphenation, sophisticated fonts and layouts
  are beyond the scope of pisa or weasyprint.
- Templates are `.odt` files (not `.html`), meaning that end-users
  dare to edit them more easily.

See also :ref:`lino.admin.appypod`.

.. rubric:: Templates

.. xfile:: appypod/Table.odt

    Template used to print a table in landscape orientation.

.. xfile:: appypod/Table-portrait.odt

    Template used to print a table in portrait orientation.

.. xfile:: appypod/Labels.odt

    Template used to print address labels.

.. rubric:: Glossary

.. glossary::
  :sorted:
  
  ODFPy
    A Python library for manipulating OpenDocument documents 
    (.odt, .ods, .odp, ...): 
    read existing files, modify, create new files from scratch.
    Read more on `PyPI <http://pypi.python.org/pypi/odfpy>`_.
    Project home page https://joinup.ec.europa.eu/software/odfpy

  appy.pod 

    A nice tool for generating pdf and other formats, including .odt
    or .doc) from .odt templates.  See
    http://appyframework.org/pod.html
  
  appypod

    As long as :term:`appy.pod` does not support Python 3, we use
    `Stefan Klug's Python 3 port
    <https://libraries.io/github/stefanklug/appypod>`_.

.. rubric:: Modules in this package

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

