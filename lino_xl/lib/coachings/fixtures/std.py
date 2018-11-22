# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""Adds default data for `CoachingEnding`.

"""

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lino.api.dd import babelkw


def objects():
    from lino.api import rt
    CoachingEnding = rt.models.coachings.CoachingEnding

    yield CoachingEnding(**babelkw('name',
                                   de="Übergabe an Kollege",
                                   fr="Transfert vers collègue",
                                   en="Transfer to colleague",))
    yield CoachingEnding(**babelkw('name',
                                   de="Einstellung des Anrechts auf SH",
                                   fr="Arret du droit à l'aide sociale",
                                   en="End of right on social aid"))
    yield CoachingEnding(**babelkw('name',
                                   de="Umzug in andere Gemeinde",
                                   fr="Déménagement vers autre commune",
                                   en="Moved to another town"))
    yield CoachingEnding(**babelkw('name',
                                   de="Hat selber Arbeit gefunden",
                                   fr="A trouvé du travail",
                                   en="Found a job"))
    
