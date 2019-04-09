# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _


def objects():
    Type = rt.models.households.Type

    yield Type(**dd.str2kw('name', _("Married couple")))
    # Verheiratet / Marié

    yield Type(**dd.str2kw('name', _("Divorced couple")))
    # Geschieden / Divorcé

    yield Type(**dd.str2kw('name', _("Factual household")))
    # Faktischer Haushalt / Ménage de fait

    yield Type(**dd.str2kw('name', _("Legal cohabitation")))
    # Legale Wohngemeinschaft / Cohabitation légale

    yield Type(**dd.str2kw('name', _("Isolated")))
    yield Type(**dd.str2kw('name', _("Other")))
