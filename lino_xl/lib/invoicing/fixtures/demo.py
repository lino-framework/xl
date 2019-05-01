# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _


def DEP(name, **kwargs):
    kwargs = dd.str2kw('designation', name, **kwargs)
    # kwargs.update(designation=name)
    return rt.models.invoicing.Area(**kwargs)


def objects():
    yield DEP(_("First"))
    yield DEP(_("Second"))
    yield DEP(_("Third"))

