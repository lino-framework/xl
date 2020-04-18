# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.api import dd, rt
from django.db.utils import OperationalError, ProgrammingError

class TrendObservable(dd.Model):
    class Meta:
        abstract = True

    @classmethod
    def on_analyze(cls, site):
        super(TrendObservable, cls).on_analyze(site)
        TrendEvent = rt.models.trends.TrendEvent
        def w(ts):
            # return a getter function that returns the date of the first event
            # of the given trend stage.
            def func(obj, ar):
                qs = TrendEvent.objects.filter(subject=obj, trend_stage=ts)
                te = qs.order_by('event_date').first()
                if te is not None:
                    return te.event_date
            return func
        try:
            for ts in rt.models.trends.TrendStage.objects.filter(subject_column=True):
                name = "trend_date_" + str(ts.id)
                vf = dd.VirtualField(dd.DateField(str(ts)), w(ts), wildcard_data_elem=True)
                cls.define_action(**{name: vf})
        except (OperationalError, ProgrammingError) as e:
            # Error can differ depending on the database engine.
            dd.logger.debug("Failed to load trend stages : %s", e)
