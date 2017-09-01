# -*- coding: UTF-8 -*-
# Copyright 2014-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)
"""
Database models for `lino_xl.lib.appypod`.

"""

from lino.api import dd, rt
from lino.core.tables import AbstractTable

from .choicelists import *
from .mixins import (PrintTableAction, PortraitPrintTableAction,
                     PrintLabelsAction)

AbstractTable.as_pdf = PrintTableAction()
AbstractTable.as_pdf_p = PortraitPrintTableAction()

from lino.utils.addressable import Addressable
Addressable.print_labels = PrintLabelsAction()

# @dd.receiver(dd.pre_analyze)
# def customize_contacts1(sender, **kw):
#     from lino.utils.addressable import Addressable
#     for m in rt.models_by_base(Addressable):
#         m.define_action(print_labels=PrintLabelsAction())
#     # if sender.is_installed('contacts'):
#     #     sender.modules.contacts.Partner.define_action(
#     #         print_labels=PrintLabelsAction())

