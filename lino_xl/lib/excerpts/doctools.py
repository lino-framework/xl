# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""
A function for usage in a :rst:dir:`py2rst` directive.

This is used to generate the list of demo excerpts in the following
page:

- https://de.welfare.lino-framework.org/excerpts.html
- https://welfare.lino-framework.org/specs/aids/
"""


import os
import shutil
from pathlib import Path
import rstgen
from lino.api import rt
from django.conf import settings

def show_excerpts(severe=True):
    ses = rt.login()
    # dd.logger.info("20141029 %s", settings.SITE)
    coll = {}

    def collect(obj):
        l = coll.setdefault(obj.excerpt_type, [])
        mf = obj.build_method.get_target(None, obj)
        tmppath  = Path(mf.name)
        if tmppath.exists():
            tail = tmppath.name
            tail = 'dl/excerpts/' + tail
            kw = dict(tail=tail)
            kw.update(type=obj.excerpt_type)
            kw.update(owner=obj.owner)
            try:
                # dd.logger.info("20141029 copy %s to %s", tmppath, tail)
                shutil.copyfile(tmppath, tail)
            except IOError as e:
                kw.update(error=str(e))
                msg = "%(type)s %(owner)s %(tail)s Oops: %(error)s" % kw
                # raise Exception(msg)
                kw.update(owner=msg)

            l.append(kw)

    for o in rt.models.excerpts.Excerpt.objects.order_by('excerpt_type'):
        collect(o)

    def asli(et, items):
        s = str(et)
        s += " : " + ', '.join(
            "`%(owner)s <../%(tail)s>`__" % kw % kw for kw in items)
        return s

    return rstgen.ul([asli(k, v) for k, v in coll.items()])
