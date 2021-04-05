# -*- coding: UTF-8 -*-
# Copyright 2014-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Makes sure that there is at least one excerpt for every ExcerptType.
Render all excerpts by running their do_print method.

"""

import traceback

from lino.api import rt, dd

SEVERE = True


def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    Excerpt = rt.models.excerpts.Excerpt

    if not dd.plugins.excerpts.responsible_user:
        return

    ses = rt.login(dd.plugins.excerpts.responsible_user)

    for et in ExcerptType.objects.all().order_by('id'):
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
