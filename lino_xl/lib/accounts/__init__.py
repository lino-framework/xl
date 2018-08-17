# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/accounts`.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Accounting")
    needs_plugins = ['lino_xl.lib.xl']  # translations

    ref_length = 20

    def __init__(self, *args):
        super(Plugin, self).__init__(*args)
        if hasattr(self.site, 'accounts_ref_length'):
            v = self.site.accounts_ref_length
            raise Exception("""%s has an attribute 'accounts_ref_length'!.
You probably want to replace this by:
ad.configure_plugins("accounts", ref_length=%r)
""" % (self.site, v))

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        # m.add_action('accounts.AccountCharts')
        if False:
            for ch in site.modules.accounts.AccountCharts.items():
                m.add_action(
                    site.modules.accounts.GroupsByChart, master_instance=ch)
        m.add_action('accounts.Groups')
        m.add_action('accounts.Accounts')

    # def setup_explorer_menu(self, site, user_type, m):
    #     mg = self
    #     m = m.add_menu(mg.app_label, mg.verbose_name)
    #     m.add_action('accounts.CommonAccounts')
