# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Adds functionality for importing BankToCustomer SEPA statements
from a bank.  See :doc:`/specs/b2c`.


.. autosummary::
    :toctree:

    camt
    febelfin
    fixtures.demo

"""

from __future__ import unicode_literals

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("SEPA import")

    needs_plugins = ['lino_cosi.lib.cosi']

    import_statements_path = None
    """
    The full name of the directory that Lino should watch for incoming xml files
    that need to get imported.
    """

    delete_imported_xml_files = False
    """This attribute define whether, Cosi have to delete the SEPA file
    after it get imported.

    """

    def setup_main_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('system.SiteConfig', 'import_b2c')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.sepa
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('b2c.Accounts')
        m.add_action('b2c.Statements')
        m.add_action('b2c.Transactions')
