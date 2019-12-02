# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd

from lino.api import dd, rt, _

def objects():
    ExcerptType = rt.models.excerpts.ExcerptType

    kw = dict(
        template="default.weasy.html",
        primary=True, certifying=True,
        build_method='weasy2pdf',
        **dd.str2kw('name', _("VAT declaration")))
    yield ExcerptType.update_for_model(rt.models.bevats.Declaration, **kw)
