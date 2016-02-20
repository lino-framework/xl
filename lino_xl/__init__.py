# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""This is the main module of Lino XL.

.. autosummary::
   :toctree:

   lib
   projects


"""

import os

execfile(os.path.join(os.path.dirname(__file__), 'setup_info.py'))
__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://xl.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/xl/blob/master/%s'

