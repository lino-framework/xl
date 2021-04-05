# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Creates a certifying :class:`ExcerptType` instance for every model
that inherits from :class:`Certifiable`.

"""

from lino.api import dd, rt
from lino_xl.lib.excerpts.mixins import Certifiable


def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    ContentType = rt.models.contenttypes.ContentType
    for cls in rt.models_by_base(Certifiable):
        ct = ContentType.objects.get_for_model(cls)
        kw = dict(content_type=ct, primary=True, certifying=True)
        if ExcerptType.objects.filter(**kw).count() == 0:
            kw.update(dd.str2kw('name', cls._meta.verbose_name))
            yield ExcerptType(**kw)
