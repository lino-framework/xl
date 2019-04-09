# Copyright 2014-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/sepa`.

.. autosummary::
   :toctree:

    utils
    fields
    roles
    fixtures.sample_ibans

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("SEPA")
    site_js_snippets = ['iban/uppercasetextfield.js']
    needs_plugins = ['lino_xl.lib.ledger']

    def setup_explorer_menu(self, site, user_type, m):
        mg = self
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sepa.Accounts')
