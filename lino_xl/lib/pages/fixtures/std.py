# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""

Default data for `pages` is the content defined in 
:mod:`lino_xl.lib.pages.fixtures.web`.

"""
#~ from lino_xl.lib.pages.fixtures.web import objects


def objects():

    from lino_xl.lib.pages.fixtures.intro import objects
    yield objects()

    #~ from lino_xl.lib.pages.fixtures.man import objects
    #~ yield objects()
