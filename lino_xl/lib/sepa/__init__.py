# Copyright 2014-2015 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


"""Adds models and tables for managing bank accounts for your
partners.  It requires the :mod:`lino_xl.lib.contacts` plugin.

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

    def setup_explorer_menu(self, site, profile, m):
        mg = self
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('sepa.Accounts')
