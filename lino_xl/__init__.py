# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""The :mod:`lino_xl` package contains a library of extended plugins
to be used by Lino applications.

.. autosummary::
   :toctree:

   lib

"""

import os

fn = os.path.join(os.path.dirname(__file__), 'setup_info.py')
exec(compile(open(fn, "rb").read(), fn, 'exec'))

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://www.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/xl/blob/master/%s'

