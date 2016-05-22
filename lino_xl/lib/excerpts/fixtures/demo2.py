# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.
"""Makes sure that there is at least one excerpt for every ExcerptType.
Render all excerpts by running their do_print method.

"""
import traceback

from lino.api import rt, dd

from lino_xl.lib.excerpts.mixins import Certifiable

PRINT_THEM_ALL = True
SEVERE = True


def objects():
    ExcerptType = rt.modules.excerpts.ExcerptType
    Excerpt = rt.modules.excerpts.Excerpt

    if not dd.plugins.excerpts.responsible_user:
        return

    ses = rt.login(dd.plugins.excerpts.responsible_user)

    for et in ExcerptType.objects.all():
        model = et.content_type.model_class()
        if issubclass(model, Certifiable):
            qs = model.get_printable_demo_objects(et)
        else:
            qs = model.objects.all()
            if qs.count() > 0:
                qs = [qs[0]]

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
        except Exception as e:
            if SEVERE:
                raise
            else:
                traceback.print_exc(e)
                dd.logger.warning(
                    "20160311 failed to render %s : %s", obj, e)

