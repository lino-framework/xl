# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Adds functionality for handling incoming and outgoing invoices in a
context where the site operator is subject to value-added tax
(VAT). Site operators outside the European Union are likely to use 
:mod:`lino_xl.lib.vatless` instead.

Installing this plugin will automatically install
:mod:`lino_xl.lib.countries` :mod:`lino_xl.lib.ledger`.

The modules :mod:`lino_xl.lib.vatless` and :mod:`lino_xl.lib.vat` can
theoretically both be installed (though obviously this wouldn't make
much sense).


.. autosummary::
   :toctree:

    models
    desktop
    choicelists
    utils
    mixins
    fixtures.novat
    fixtures.euvatrates

"""

from django.utils.translation import ugettext_lazy as _
from lino.api import ad
import six

class Plugin(ad.Plugin):
    """See :class:`lino.core.plugin.Plugin`.

    """
    verbose_name = _("VAT")

    needs_plugins = ['lino_xl.lib.countries', 'lino_xl.lib.ledger']

    # vat_quarterly = False
    # """
    # Set this to True to support quarterly VAT declarations.
    # Used by :mod:`lino_xl.lib.declarations`.
    # """

    default_vat_regime = 'private'
    """The default VAT regime. If this is specified as a string, Lino will
    resolve it at startup into an item of :class:`VatRegimes
    <lino_xl.lib.vat.choicelists.VatRegimes>`.

    """

    default_vat_class = 'normal'
    """The default VAT class. If this is specified as a string, Lino will
    resolve it at startup into an item of :class:`VatClasses
    <lino_xl.lib.vat.choicelists.VatClasses>`.

    """

    def get_vat_class(self, tt, item):
        """Return the VAT class to be used for given trade type and given
invoice item. Return value must be an item of
:class:`lino_xl.lib.vat.models.VatClasses`.

        """
        return self.default_vat_class

    def on_site_startup(self, site):
        vat = site.modules.vat
        if isinstance(self.default_vat_regime, six.string_types):
            self.default_vat_regime = vat.VatRegimes.get_by_name(
                self.default_vat_regime)
        if isinstance(self.default_vat_class, six.string_types):
            self.default_vat_class = vat.VatClasses.get_by_name(
                self.default_vat_class)

    def setup_config_menu(config, site, user_type, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        m.add_action('vat.VatRules')

    def setup_explorer_menu(config, site, user_type, m):
        m = m.add_menu(config.app_label, config.verbose_name)
        m.add_action('vat.VatRegimes')
        m.add_action('vat.VatClasses')

