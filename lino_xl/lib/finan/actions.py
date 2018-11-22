# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import re

from django.conf import settings

from lino.api import dd, rt, _

from lino.modlib.printing.mixins import DirectPrintAction
from etgen.sepa.validate import validate_pain001

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
    
    def get_printable_context(self, bm, elem, ar):
        context = super(
            WritePaymentsInitiation, self).get_printable_context(
                bm, elem, ar)
        sc = settings.SITE.site_config.site_company
        if not sc:
            raise Warning(_("You must specify a site owner"))
        if sc.vat_id:
            # raise Warning(_("Site owner has no national ID"))
            # if not sc.vat_id.startswith("BE-"):
            #     raise Warning(_("Site owner has invalid ID {}").format(
            #         sc.vat_id))
            # our_id = sc.vat_id[3:]
            our_id = re.sub('[^0-9]', '', sc.vat_id[3:])
            context.update(our_name=str(sc))
            context.update(our_id=our_id)
            context.update(our_issuer='KBO-BCE')
        # raise Exception(str(context))
        return context
    
    def before_build(self, bm, elem):
        # if not elem.execution_date:
        #     raise Warning(_("You must specify an execution date"))
        acc = elem.journal.sepa_account
        if not acc:
            raise Warning(
                _("Journal {} has no SEPA account").format(elem.journal))
        if not acc.bic:
            raise Warning(
                _("SEPA account for journal {} has no BIC").format(
                    elem.journal))
        
        return super(WritePaymentsInitiation, self).before_build(bm, elem)

    def validate_result_file(self, filename):
        try:
            validate_pain001(filename)
        except Exception as e:
            raise Warning(_(
                "Oops, the generated XML file {} is invalid: {}").format(
                    filename, e))
