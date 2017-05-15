# Copyright 2008-2016 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds functionality for managing financial vouchers.  
See :doc:`/specs/cosi/finan`.

.. autosummary::
   :toctree:

    models
    choicelists
    mixins
    fixtures.payments

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    """This :class:`Plugin <lino.core.plugin.Plugin>` class adds some
    entries to the Explorer menu.  It contains the following
    additional attributes:

    .. attribute:: suggest_future_vouchers

        Whether to suggest vouchers whose due_date is in the future.

        The default value is currently `False` because some demo fixtures
        rely on this.  But in most cases this should probably be set to
        `True` because of course a customer can pay an invoice in advance.

        You can specify this for your application::

            def setup_plugins(self):
                self.plugins.finan.suggest_future_vouchers = True
                super(Site, self).setup_plugins()

        Or, as a local system administrator you can also simply set it
        after your :data:`SITE` instantiation::

            SITE = Site(globals())
            ...
            SITE.plugins.finan.suggest_future_vouchers = True

    """

    verbose_name = _("Financial")
    needs_plugins = ['lino_xl.lib.ledger']
    suggest_future_vouchers = False

    # def setup_main_menu(self, site, profile, m):
    #     m = m.add_menu(self.app_label, self.verbose_name)
    #     ledger = site.modules.ledger
    #     for jnl in ledger.Journal.objects.filter(trade_type=''):
    #         m.add_action(jnl.voucher_type.table_class,
    #                      label=unicode(jnl),
    #                      params=dict(master_instance=jnl))

    def setup_explorer_menu(self, site, profile, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('finan.AllBankStatements')
        m.add_action('finan.AllJournalEntries')
        m.add_action('finan.AllPaymentOrders')
        # m.add_action('finan.Groupers')
