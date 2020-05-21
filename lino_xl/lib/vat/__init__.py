# -*- coding: UTF-8 -*-
# Copyright 2013-2019 Rumma & Ko
# License: BSD (see file COPYING for details)


"""See :doc:`/specs/vat`.

.. autosummary::
   :toctree:

    utils


"""

from django.utils.translation import ugettext_lazy as _
from lino.api import ad
import six

class Plugin(ad.Plugin):
    """The :class:`Plugin <lino.core.plugin.Plugin>` object for this
    plugin.

    """
    verbose_name = _("VAT")
    # menu_group = "vat"

    needs_plugins = ['lino.modlib.checkdata', 'lino_xl.lib.excerpts']

    eu_country_codes = """AT BE BG CY CZ DK DE EE ES FI FR GB GR HU HR IE IT LV
    LT LU MT NL PO PT RO SE SI SK"""

    """A space-separated list of ISO codes that are to be considered part of
    the EU. This is used to define the VAT area of a partner, which in turn
    influences the available VAT regimes.  See
    :class:`lino_xl.lib.vat.VatAreas`.

    When a member state leaves or joins the EU (and you have partners there),
    you can either update your Lino (we plan to keep this list up to date), or
    you can change it locally.

    At site startup this is converted from a string to a set. Duplicate codes
    are ignored. For example so in your :attr:`layouts_module
    <lino.core.site.Site.layouts_module>` you may write code like this::

        if brexit:
            dd.plugins.vat.eu_country_codes.remove("GB")

    The :attr:`isocode <lino_xl.lib.countries.Country.isocode>` fields in your
    :class:`countries.Countries <lino_xl.lib.countries.Countries>` table must
    match the codes specified here.

    """

    default_vat_regime = 'normal'
    """The default VAT regime. If this is specified as a string, Lino will
    resolve it at startup into an item of :class:`VatRegimes
    <lino_xl.lib.vat.VatRegimes>`.

    """

    default_vat_class = 'services'
    """The default VAT class. If this is specified as a string, Lino will
    resolve it at startup into an item of :class:`VatClasses
    <lino_xl.lib.vat.VatClasses>`.

    """

    declaration_plugin = None
    """The plugin to use as your :term:`national declaration module`.

    Available VAT declaration plugins are:
    :mod:`lino_xl.lib.bevat`,
    :mod:`lino_xl.lib.bevats` and
    :mod:`lino_xl.lib.eevat`.

    This can remain `None` e.g. in applicatons that use the ledger plugin for
    orders or invoicing, but don't care about general accounting functionality.

    """

    item_vat = False
    """Whether item prices in trade documents are meant VAT included.
    """

    def get_vat_class(self, tt, item):
        """Return the VAT class to be used for given trade type and given
        invoice item. Return value must be an item of
        :class:`lino_xl.lib.vat.VatClasses`.

        """
        return self.default_vat_class

    def get_required_plugins(self):

        for p in super(Plugin, self).get_required_plugins():
            yield p

        yield 'lino_xl.lib.countries'

        # vat needs ledger but doesn't declare this dependency to avoid
        # having ledger before sales in menus:
        yield 'lino_xl.lib.ledger'

        if self.declaration_plugin is not None:
            yield self.declaration_plugin
            # if isinstance(self.declaration_plugins, six.string_types):
            #     self.declaration_plugins = self.declaration_plugins.split()
            # for i in self.declaration_plugins:
            #     yield i

    def on_site_startup(self, site):
        vat = site.modules.vat
        if isinstance(self.eu_country_codes, six.string_types):
            self.eu_country_codes = set(self.eu_country_codes.split())
        if isinstance(self.default_vat_regime, six.string_types):
            self.default_vat_regime = vat.VatRegimes.get_by_name(
                self.default_vat_regime)
        if isinstance(self.default_vat_class, six.string_types):
            self.default_vat_class = vat.VatClasses.get_by_name(
                self.default_vat_class)

    def setup_reports_menu(self, site, user_type, m):
        if self.declaration_plugin is None:
            return
        # mg = site.plugins.ledger
        # mg = site.plugins.vat
        mg = self  # don't merge into sales menus for reports
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('vat.PrintableInvoicesByJournal')
        m.add_action('vat.IntracomPurchases')
        m.add_action('vat.IntracomSales')


    def setup_explorer_menu(self, site, user_type, m):
        mg = self  # don't merge into sales menus for explorer
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('vat.VatAreas')
        m.add_action('vat.VatRegimes')
        m.add_action('vat.VatClasses')
        m.add_action('vat.VatColumns')
        m.add_action('vat.Invoices')
        m.add_action('vat.VatRules')
        # m.add_action('vat.InvoiceItems')
