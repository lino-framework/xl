# -*- coding: UTF-8 -*-
# Copyright 2018-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import rt

def objects():

    ExcerptType = rt.models.excerpts.ExcerptType
    yield ExcerptType.update_for_model(
        rt.models.sheets.Report, build_method='weasy2pdf')
