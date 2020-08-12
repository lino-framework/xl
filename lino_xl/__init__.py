# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""This package contains the code of the :ref:`xl`.

See :ref:`specs.xl` for the list of plugins.

.. autosummary::
   :toctree:

   lib

"""

import os

from lino_xl.setup_info import SETUP_INFO

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="http://xl.lino-framework.org")
srcref_url = 'https://github.com/lino-framework/xl/blob/master/%s'
doc_trees = ['docs']
