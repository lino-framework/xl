# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""This package contains the code of the :ref:`xl`.

.. autosummary::
   :toctree:

   lib

"""

import os

fn = os.path.join(os.path.dirname(__file__), 'setup_info.py')
exec(compile(open(fn, "rb").read(), fn, 'exec'))

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://xl.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/xl/blob/master/%s'
doc_trees = ['docs']
