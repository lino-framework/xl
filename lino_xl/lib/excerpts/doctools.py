# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""
A function for usage in a :rst:dir:`django2rst` directive.

This is used to generate the list of demo excerpts in the following
page:

- http://de.welfare.lino-framework.org/excerpts.html
"""


import os
import shutil
import rstgen
from lino.api import rt
from django.conf import settings

def show_excerpts(severe=True):
    ses = rt.login()
    # dd.logger.info("20141029 %s", settings.SITE)
    coll = {}

    def collect(obj):
        l = coll.setdefault(obj.excerpt_type, [])
        if len(l) > 2:
            return
        try:
            rv = ses.run(obj.do_print)
        except Warning as e:
            return
        if rv['success']:
            pass
            # print("\n\n%s\n\n" % rv['open_url'])
        else:
            if severe:
                raise Exception("Oops: %s" % rv['message'])
            else:
                return
        if not 'open_url' in rv:
            if severe:
                raise Exception("Oops: %s" % rv['message'])
            else:
                return

        # tmppath = settings.SITE.project_dir + rv['open_url']
        tmppath = settings.SITE.cache_dir
        if not 'media' in rv['open_url']:
        # if not tmppath.endswith('media'):
            tmppath = tmppath.child('media')
        tmppath += rv['open_url']
        head, tail = os.path.split(tmppath)
        # tail = 'tested/' + tail
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
