# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, _

class HealthcareClient(dd.Model):

    class Meta:
        abstract = True

    healthcare_plan = dd.ForeignKey(
        'healthcare.Plan', blank=True, null=True)
