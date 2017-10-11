# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from django.db import models

from lino.api import dd, rt, _

from lino.modlib.printing.mixins import DirectPrintAction

class WriteXML(DirectPrintAction):
    """Generate an XML file from this database object.

    """
    combo_group = "writexml"
    label = _("XML")
    
    build_method = "xml"
    icon_name = None
    # show_in_bbar = False


class WritePaymentsInitiation(WriteXML):
    """Generate an XML file (SEPA payment initiation) from this database
object.

    """

    tplname = "pain_001"
    
    def before_build(self, bm, elem):
        if not elem.execution_date:
            raise Warning(_("You must specify an execution date"))
        acc = elem.journal.sepa_account
        if not acc:
            raise Warning(
                _("Journal {} has no SEPA account").format(elem.journal))
        if not acc.bic:
            raise Warning(
                _("SEPA account for journal {} has no BIC").format(
                    elem.journal))
        
        return super(WritePaymentsInitiation, self).before_build(bm, elem)

