# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre

from lino.api import dd, rt, _

def objects():
    ExcerptType = rt.modules.excerpts.ExcerptType
    ContentType = rt.modules.contenttypes.ContentType

    yield ExcerptType(
        template="default.weasy.html",
        primary=True, certifying=True,
        build_method='weasy2pdf',
        content_type=ContentType.objects.get_for_model(
            dd.resolve_model('bevats.Declaration')),
        **dd.str2kw('name', _("VAT declaration")))



