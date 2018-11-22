# -*- coding: UTF-8 -*-
# Copyright 2016 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
from __future__ import unicode_literals
from __future__ import print_function

from lino.api import rt, dd


def objects():
    SessionType = rt.models.working.SessionType
    yield SessionType(id=1, name="Default")

    ServiceReport = rt.models.working.ServiceReport
    ExcerptType = rt.models.excerpts.ExcerptType
    kw = dict(
        build_method='weasy2html',
        # template='service_report.weasy.html',
        # body_template='default.body.html',
        # print_recipient=False,
        primary=True, certifying=True)
    kw.update(dd.str2kw('name', ServiceReport._meta.verbose_name))
    yield ExcerptType.update_for_model(ServiceReport, **kw)
