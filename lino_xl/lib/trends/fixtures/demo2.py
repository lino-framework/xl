# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

# add some trend events for each subject

from lino.utils import Cycler
from lino.api import rt, dd

def objects():
    if dd.plugins.trends.subject_model is None:
        return
    TrendStage = rt.models.trends.TrendStage
    TrendEvent = rt.models.trends.TrendEvent

    STAGES = Cycler(TrendStage.objects.all())

    if len(STAGES) == 0:
        return

    offset = -200
    for obj in dd.plugins.trends.subject_model.objects.all():
        for i in range(3):
            yield TrendEvent(event_date=dd.today(offset), subject=obj, trend_stage=STAGES.pop())
            offset += 1
