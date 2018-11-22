# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd

from lino.api import dd, rt, _

def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    ContentType = rt.models.contenttypes.ContentType

    yield ExcerptType(
        template="default.weasy.html",
        primary=True, certifying=True,
        build_method='weasy2pdf',
        content_type=ContentType.objects.get_for_model(
            dd.resolve_model('bevats.Declaration')),
        **dd.str2kw('name', _("VAT declaration")))



