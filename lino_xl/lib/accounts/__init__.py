# -*- coding: UTF-8 -*-
# Copyright 2013-2016 Luc Saffre
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


"""The top-level plugin for doing accounting stuff with a Lino
application.

We plan to merge this module into :mod:`lino_xl.lib.ledger` one day.

.. autosummary::
    :toctree:

    choicelists
    models
    utils
    fields

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Accounting")

    needs_plugins = ['lino_cosi.lib.cosi']  # translations

    ref_length = 20
    """The `max_length` of the `Reference` field of an account.
    """

    def __init__(self, *args):
        super(Plugin, self).__init__(*args)
        if hasattr(self.site, 'accounts_ref_length'):
            v = self.site.accounts_ref_length
            raise Exception("""%s has an attribute 'accounts_ref_length'!.
You probably want to replace this by:
ad.configure_plugins("accounts", ref_length=%r)
""" % (self.site, v))

    def setup_config_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        # m.add_action('accounts.AccountCharts')
        if False:
            for ch in site.modules.accounts.AccountCharts.items():
                m.add_action(
                    site.modules.accounts.GroupsByChart, master_instance=ch)
        m.add_action('accounts.Groups')
        m.add_action('accounts.Accounts')

