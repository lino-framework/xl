# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
# License: BSD (see file COPYING for details)
"""
Database models for `lino_xl.lib.appypod`.

This installs printing actions into all tables.

If `contacts` is installed, it installs a 
PrintLabelsAction


"""

from lino.api import dd, rt
from lino.core.tables import AbstractTable

from .choicelists import *
from .mixins import (PrintTableAction, PortraitPrintTableAction,
                     PrintLabelsAction)

AbstractTable.as_pdf = PrintTableAction()
AbstractTable.as_pdf_p = PortraitPrintTableAction()


@dd.receiver(dd.pre_analyze)
def customize_contacts1(sender, **kw):
    from lino.utils.addressable import Addressable
    for m in rt.models_by_base(Addressable):
        m.define_action(print_labels=PrintLabelsAction())
    # if sender.is_installed('contacts'):
    #     sender.modules.contacts.Partner.define_action(
    #         print_labels=PrintLabelsAction())

