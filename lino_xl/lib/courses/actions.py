# -*- coding: UTF-8 -*-
# Copyright 2016-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models

from lino.api import dd, rt, _

from lino.modlib.printing.mixins import DirectPrintAction
from lino.mixins.periods import Monthly

class PrintPresenceSheet(DirectPrintAction):
    """Action to print a presence sheet.
    """
    combo_group = "creacert"
    label = _("Presence sheet")
    tplname = "presence_sheet"
    build_method = "weasy2pdf"
    icon_name = None
    # show_in_bbar = False
    parameters = Monthly(
        show_remarks=models.BooleanField(
            _("Show remarks"), default=False),
        show_states=models.BooleanField(
            _("Show states"), default=True))
    params_layout = """
    start_date
    end_date
    show_remarks
    show_states
    """
    # keep_user_values = True
