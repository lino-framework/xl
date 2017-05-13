# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from django.db import models

from lino.api import dd, rt, _

from lino.modlib.printing.mixins import DirectPrintAction

class WriteXML(DirectPrintAction):
    """Action to generate an XML file.
    """
    combo_group = "writexml"
    label = _("Write XML")
    
    build_method = "xml"
    icon_name = None
    # show_in_bbar = False


