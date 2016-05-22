# -*- coding: UTF-8 -*-
# Copyright 2014-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.
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

