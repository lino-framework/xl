# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
A :term:`dummy module` for `postings`, used by 
"""

from lino.api import dd


class Postable(object):
    pass

PostingsByController = dd.DummyField
