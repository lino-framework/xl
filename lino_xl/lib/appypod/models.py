# Copyright 2014-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt
from lino.core.tables import AbstractTable

from .choicelists import *
from .mixins import (PrintTableAction, PortraitPrintTableAction,
                     PrintLabelsAction)

AbstractTable.as_pdf = PrintTableAction()
AbstractTable.as_pdf_p = PortraitPrintTableAction()

from lino.utils.addressable import Addressable
Addressable.print_labels = PrintLabelsAction()

