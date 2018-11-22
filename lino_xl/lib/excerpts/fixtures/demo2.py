# -*- coding: UTF-8 -*-
# Copyright 2014-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""Makes sure that there is at least one excerpt for every ExcerptType.
Render all excerpts by running their do_print method.

"""
from __future__ import unicode_literals

import traceback

from lino.api import rt, dd

# from lino_xl.lib.excerpts.mixins import Certifiable

PRINT_THEM_ALL = True
SEVERE = True


def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    Excerpt = rt.models.excerpts.Excerpt

    if not dd.plugins.excerpts.responsible_user:
        return

    ses = rt.login(dd.plugins.excerpts.responsible_user)

    for et in ExcerptType.objects.all():
        model = et.content_type.model_class()
        qs = model.get_printable_demo_objects()
        # if issubclass(model, Certifiable):
        #     qs = model.get_printable_demo_objects(et)
        # else:
        #     qs = model.objects.all()
        #     if qs.count() > 0:
        #         qs = [qs[0]]
        # if et.certifying:
        for obj in qs:
            ses.selected_rows = [obj]
            yield et.get_or_create_excerpt(ses)
        # qs2 = Excerpt.objects.filter(excerpt_type=et)
        # if qs2.count() == 0:
        #     if qs.count() > 0:
        #         ses.selected_rows = [qs[0]]
        #         yield et.get_or_create_excerpt(ses)

    for obj in Excerpt.objects.all():
        # dd.logger.info("20150526 rendering %s", obj)
        try:
            rv = ses.run(obj.do_print)
            assert rv['success']
        except Warning as e:
            dd.logger.warning(
                "Failed to render %s : %s", obj, e)
        except Exception as e:
            if SEVERE:
                raise
            else:
                traceback.print_exc()
                dd.logger.warning(
                    "20160311 failed to render %s : %s", obj, e)

