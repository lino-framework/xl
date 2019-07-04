# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""This is Lino's standard plugin for General Ledger.
See :doc:`/specs/ledger`.

.. autosummary::
    :toctree:

    roles
    fields
    management.commands.reregister

"""

from __future__ import unicode_literals

from django.utils.functional import lazystr

from lino.api import ad, _

UPLOADTYPE_SOURCE_DOCUMENT = 1
"""Primary key  of upload type "source document" created in :fixture:`std` fixture."""


class Plugin(ad.Plugin):

    verbose_name = _("Accounting")
    needs_plugins = ['lino.modlib.weasyprint', 'lino_xl.lib.xl', 'lino.modlib.uploads']

    ref_length = 4  # 20
    """
    The `max_length` of the `Reference` field of an account.
    """

    currency_symbol = "€"
    """
    Temporary approach until we add support for multiple currencies.
    See also :meth:`lino.core.site.Site.format_currency`.
    """
    
    use_pcmn = False
    """
    Whether to use the PCMN notation.

    PCMN stands for "plan compatable minimum normalisé" and is a
    standardized nomenclature for accounts used in France and
    Belgium.

    """
    project_model = None
    """
    Leave this to `None` for normal behaviour.  Set this to a
    string of the form `'<app_label>.<ModelName>'` if you want to
    add an additional field `project` to all models which inherit
    from :class:`lino_xl.lib.ledger.ProjectRelated`.
    """
    
    # intrusive_menu = False
    # """
    # Whether the plugin should integrate into the application's
    # main menu in an intrusive way.  Intrusive means that the main
    # menu gets one top-level item per journal group.
    #
    # The default behaviour is `False`, meaning that these items are
    # gathered below a single item "Accounting".
    # """
    #
    start_year = 2012
    """
    An integer with the calendar year in which this site starts
    working.

    This is used to fill the default list of :class:`FiscalYears`,
    and by certain fixtures for generating demo invoices.
    """
    
    fix_y2k = False
    """
    Whether to use a Y2K compatible representation for fiscal years.
    """
    
    suppress_movements_until = None
    """
    Don't create any movements before that date.  Vouchers can exist
    and get registered before that date, but they don't have any
    influence to the ledger.

    This is useful e.g. when you want to keep legacy vouchers in your
    database but not their movments.
    """

    sales_stories = True
    """Whether demo fixtures should generate manual sales invoices."""

    purchase_stories = True
    """Whether demo fixture should generate purchase invoices."""

    def post_site_startup(self, site):
        super(Plugin, self).post_site_startup(site)
        site.models.ledger.CommonAccounts.sort()
        site.models.ledger.VoucherTypes.sort()

    def setup_main_menu(self, site, user_type, m):
        """
        Add a menu item for every journal.

        Menu items are grouped by journal group. See :class:`lino_xl.lib.ledger.JournalGroups`

        """
        Journal = site.models.ledger.Journal
        JournalGroups = site.models.ledger.JournalGroups
        for grp in JournalGroups.get_list_items():
            mg = grp.menu_group
            if mg is None:
                lp = site.plugins.ledger
                lm = m.add_menu(lp.app_label, lp.verbose_name)
                subm = lm.add_menu(grp.name, grp.text)
            else:
                subm = m.add_menu(mg.app_label, mg.verbose_name)
            for jnl in Journal.objects.filter(
                    journal_group=grp).order_by('seqno'):
                subm.add_action(jnl.voucher_type.table_class,
                                label=lazystr(jnl),
                                params=dict(master_instance=jnl))

    def setup_reports_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m.add_action('ledger.Situation')
        # m.add_action('ledger.ActivityReport')
        # m.add_action('ledger.AccountingReport')
        # m.add_action('ledger.GeneralAccountBalances')
        # m.add_action('ledger.CustomerAccountBalances')
        # m.add_action('ledger.SupplierAccountBalances')
        m.add_action('ledger.Debtors')
        m.add_action('ledger.Creditors')

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ledger.Accounts')
        m.add_action('ledger.Journals')
        m.add_action('ledger.FiscalYears')
        m.add_action('ledger.AccountingPeriods')
        m.add_action('ledger.PaymentTerms')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.ledger
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ledger.CommonAccounts')
        m.add_action('ledger.MatchRules')
        m.add_action('ledger.AllVouchers')
        m.add_action('ledger.VoucherTypes')
        m.add_action('ledger.AllMovements')
        m.add_action('ledger.TradeTypes')
        m.add_action('ledger.JournalGroups')

    def remove_dummy(self, *args):
        lst = list(args)
        if self.project_model is None:
            lst.remove('project')
        return lst

