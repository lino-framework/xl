# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Installs a primary certifiable ExcerptType for Milestone.

"""

from lino.api import rt, dd


def unused_objects():
    Milestone = dd.plugins.tickets.milestone_model
    ExcerptType = rt.models.excerpts.ExcerptType

    kw = dict(
        body_template='default.body.html',
        print_recipient=False,
        primary=True, certifying=True)
    kw.update(dd.str2kw('name', Milestone._meta.verbose_name))
    yield ExcerptType.update_for_model(Milestone, **kw)
