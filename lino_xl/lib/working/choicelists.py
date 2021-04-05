# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from lino.api import dd, _

from lino.utils.quantities import ZERO_DURATION

class ReportingTypes(dd.ChoiceList):
    verbose_name = _("Reporting type")
    verbose_name_plural = _("Reporting types")


add = ReportingTypes.add_item

add('10', _("Regular"), 'regular')
add('20', _("Extra"), 'extra')
add('30', _("Free"), 'free')
# add('10', _("Worker"), 'worker')
# add('20', _("Employer"), 'employer')
# add('30', _("Customer"), 'customer')
