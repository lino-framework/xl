# -*- coding: UTF-8 -*-
# Copyright 2014-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Creates a certifying :class:`ExcerptType` instance for every model
which inherits from :class:`Certifiable`.

"""

from django.contrib.contenttypes.models import ContentType

from lino.api import dd, rt
from lino_xl.lib.excerpts.mixins import Certifiable


def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    for cls in rt.models_by_base(Certifiable):
        kw = dd.str2kw('name', cls._meta.verbose_name)
        kw.update(primary=True, certifying=True)
        yield ExcerptType(
            content_type=ContentType.objects.get_for_model(cls),
            **kw)

