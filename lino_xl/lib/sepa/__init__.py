# Copyright 2014-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Adds models and tables for managing bank accounts for your
partners.  It requires the :mod:`lino_xl.lib.ledger` plugin.

The name ``sepa`` is actually irritating because this plugin won't do
any SEPA transfer. Maybe rename it to ``iban``? OTOH it is needed by
the SEPA modules :mod:`lino_cosi.lib.b2c` and
:mod:`lino_cosi.lib.c2b`.


.. autosummary::
   :toctree:

    models
    mixins
    utils
    fields
    roles
    fixtures.demo
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
