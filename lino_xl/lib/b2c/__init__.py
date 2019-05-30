# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
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
    """A path wildcard pointing to xml files which need to get imported.

    As a system admin you can set this e.g. by specifying in your
    :xfile:`settings.py` (*before* instantiating your
    :setting:`SITE`)::

       ad.configure_plugin('b2c', import_statements_path="/var/sepa_incoming")

    End-users are supposed to download SEPA statement files to that
    directory and then to invoke the
    :class:`lino_xl.lib.b2c.models.ImportStatements` action.

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
