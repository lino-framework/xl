# -*- coding: UTF-8 -*-
# Copyright 2014-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""This is Lino's standard plugin for General Ledger.
See :doc:`/specs/cosi/ledger`.

.. autosummary::
    :toctree:

    roles
    fields
    accounts
    management.commands.reregister
    fixtures.std
    fixtures.demo
    fixtures.demo_bookings

"""

from __future__ import unicode_literals

import datetime

from lino.api import ad, _


class Plugin(ad.Plugin):

    verbose_name = _("Ledger")
    needs_plugins = ['lino_xl.lib.accounts', 'lino.modlib.weasyprint']

    currency_symbol = "€"
    use_pcmn = False
    project_model = None
    intrusive_menu = False
    start_year = 2012
    fix_y2k = False
    force_cleared_until = None

    def on_site_startup(self, site):
        if site.the_demo_date is not None:
            if self.start_year > site.the_demo_date.year:
                raise Exception(
                    "plugins.ledger.start_year is after the_demo_date")
        FiscalYears = site.modules.ledger.FiscalYears
        today = site.the_demo_date or datetime.date.today()
        for y in range(self.start_year, today.year + 6):
            FiscalYears.add_item(FiscalYears.year2value(y), str(y))

    def setup_main_menu(self, site, user_type, m):
        if not self.intrusive_menu:
            mg = site.plugins.accounts
            m = m.add_menu(mg.app_label, mg.verbose_name)

        Journal = site.models.ledger.Journal
        JournalGroups = site.models.ledger.JournalGroups
        for grp in JournalGroups.objects():
            subm = m.add_menu(grp.name, grp.text)
            for jnl in Journal.objects.filter(
                    journal_group=grp).order_by('seqno'):
                subm.add_action(jnl.voucher_type.table_class,
                                label=unicode(jnl),
                                params=dict(master_instance=jnl))

    def setup_reports_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ledger.Situation')
        m.add_action('ledger.ActivityReport')
        m.add_action('ledger.Debtors')
        m.add_action('ledger.Creditors')

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ledger.Journals')
        m.add_action('ledger.AccountingPeriods')
        m.add_action('ledger.PaymentTerms')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.accounts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ledger.MatchRules')
        m.add_action('ledger.AllVouchers')
        m.add_action('ledger.VoucherTypes')
        m.add_action('ledger.AllMovements')
        m.add_action('ledger.FiscalYears')
        m.add_action('ledger.TradeTypes')
        m.add_action('ledger.JournalGroups')


