# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Adds functionality for managing financial vouchers.  

See :doc:`/specs/finan`.

.. autosummary::
   :toctree:

    fixtures.payments

"""

from lino.api import ad, _


class Plugin(ad.Plugin):

    verbose_name = _("Financial")
    needs_plugins = ['lino_xl.lib.ledger']
    suggest_future_vouchers = False

    # def setup_main_menu(self, site, user_type, m):
    #     m = m.add_menu(self.app_label, self.verbose_name)
    #     ledger = site.modules.ledger
    #     for jnl in ledger.Journal.objects.filter(trade_type=''):
    #         m.add_action(jnl.voucher_type.table_class,
    #                      label=unicode(jnl),
    #                      params=dict(master_instance=jnl))

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('finan.AllBankStatements')
        m.add_action('finan.AllJournalEntries')
        m.add_action('finan.AllPaymentOrders')
        # m.add_action('finan.Groupers')
