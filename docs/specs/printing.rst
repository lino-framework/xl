==================
Printing documents
==================

.. How to test only this document:

     $ python setup.py test -s tests.SpecsTests.test_printing

   Initialize doctest:

    >>> from lino import startup
    >>> startup('lino_xl.projects.max.settings.doctests')
    >>> from lino.api.shell import *
    >>> from lino.api.doctest import *

The Extended Library adds a series of plugins related to printing:

- :mod:`lino_xl.lib.excerpts`.
- :mod:`lino_xl.lib.appy_pod`.
- :mod:`lino_xl.lib.wkhtmltopdf`.


>>> rt.show('printing.BuildMethods')
============= ============= ====================
 value         name          text
------------- ------------- --------------------
 latex         latex         LatexBuildMethod
 pisa          pisa          PisaBuildMethod
 rtf           rtf           RtfBuildMethod
 wkhtmltopdf   wkhtmltopdf   WkBuildMethod
 appyodt       appyodt       AppyOdtBuildMethod
 appydoc       appydoc       AppyDocBuildMethod
 appypdf       appypdf       AppyPdfBuildMethod
 appyrtf       appyrtf       AppyRtfBuildMethod
============= ============= ====================
<BLANKLINE>
