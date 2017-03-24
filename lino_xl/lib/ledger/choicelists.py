# -*- coding: UTF-8 -*-
# Copyright 2008-2016 Luc Saffre
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


"""Choicelists for `lino_xl.lib.ledger`.

"""

from django.conf import settings
from django.utils.translation import string_concat

from lino.api import dd, rt, _

from lino_xl.lib.accounts.utils import DEBIT, CREDIT
from .roles import LedgerStaff


class JournalGroups(dd.ChoiceList):
    """The list of possible journal groups.

    This list is used to build the main menu. For each journal group
    there will be a menu item in the main menu.

    Journals whose :attr:`journal_group
    <lino_xl.lib.ledger.models.Journal.journal_group>` is empty will
    not be available through the main user menu.

    The default configuration has the following journal groups:

    .. attribute:: sales

        For sales journals.

    .. attribute:: purchases

        For purchases journals.

    .. attribute:: wages

        For wages journals.

    .. attribute:: financial

        For financial journals (bank statements and cash reports)

    """
    verbose_name = _("Journal group")
    verbose_name_plural = _("Journal groups")
    required_roles = dd.login_required(LedgerStaff)

add = JournalGroups.add_item
add('10', _("Sales"), 'sales')
add('20', _("Purchases"), 'purchases')
add('30', _("Wages"), 'wages')
add('40', _("Financial"), 'financial')


class FiscalYear(dd.Choice):
    pass


class FiscalYears(dd.ChoiceList):

    """A list of the fiscal years available in this database.

    The default value for this list is 5 years starting from
    :attr:`start_year <lino_xl.lib.ledger.Plugin.start_year>`.

    If the fiscal year of your company is the same as the calendar
    year, then the default entries in this should do.  Otherwise you
    can override this in your
    :attr:`workflows_module <lino.core.site.Site.workflows_module>`.

    """
    required_roles = dd.login_required(LedgerStaff)
    item_class = FiscalYear
    verbose_name = _("Fiscal Year")
    verbose_name_plural = _("Fiscal Years")
    # ~ preferred_width = 4 # would be 2 otherwise
    max_length = 8

    @classmethod
    def year2value(cls, year):
        if dd.plugins.ledger.fix_y2k:
            if year < 2000:
                return str(year)[-2:]
            elif year < 2010:
                return "A" + str(year)[-1]
            elif year < 2020:
                return "B" + str(year)[-1]
            elif year < 2030:
                return "C" + str(year)[-1]
            else:
                raise Exception(20160304)
        return str(year)[2:]

    @classmethod
    def from_int(cls, year):
        return cls.get_by_value(cls.year2value(year))

    @classmethod
    def from_date(cls, date):
        return cls.from_int(date.year)


class PeriodStates(dd.Workflow):
    """The list of possible states of an accounting period."""
    pass

add = PeriodStates.add_item
add('10', _("Open"), 'open')
add('20', _("Closed"), 'closed')


class VoucherType(dd.Choice):
    """Base class for all items of :class:`VoucherTypes`.
    
    The **voucher type** --in a simplified approach-- defines the
    database model used to store vouchers of this type
    (:attr:`model`).

    But it can be more complex: actually the voucher type is defined
    by its :attr:`table_class`, i.e. application developers can define
    more than one *voucher type* per model by providing alternative
    tables (views) for it.

    Every Lino Cosi application has its own global list of voucher
    types defined in the :class:`VoucherTypes` choicelist.

    .. attribute:: model

        The database model used to store vouchers of this type.
        A subclass of :class:`lino_xl.lib.ledger.models.Voucher``.

    .. attribute:: table_class

        Must be a table on :attr:`model` and with `master_key` set to
        the
        :attr:`journal<lino_xl.lib.ledger.models.Voucher.journal>`.

    """
    def __init__(self, model, table_class, text=None):
        self.table_class = table_class
        model = dd.resolve_model(model)
        self.model = model
        # value = dd.full_model_name(model)
        value = str(table_class)
        if text is None:
            # text = model._meta.verbose_name + ' (%s)' % dd.full_model_name(model)
            # text = model._meta.verbose_name + ' (%s.%s)' % (
            text = string_concat(model._meta.verbose_name, " (", value, ")")
        #     model.__module__, model.__name__)
        name = None
        super(VoucherType, self).__init__(value, text, name)

    def get_items_model(self):
        """Returns the class object of the model used for storing items of
        vouchers of this type.

        """
        return self.model.items.rel.related_model

    def get_items_table(self):
        lh = self.table_class.detail_layout.get_layout_handle(
            settings.SITE.kernel.default_ui)
        from lino.modlib.extjs.elems import GridElement
        for e in lh.walk():
            print(repr(e), e.__class__)
            if isinstance(e, GridElement):
                return e

    def get_journals(self, **kwargs):
        """Return a list of the :class:`Journal` objects that work on this
        voucher type.

        """
        kwargs.update(voucher_type=self)
        return rt.modules.ledger.Journal.objects.filter(**kwargs)


class VoucherTypes(dd.ChoiceList):
    """A list of the available voucher types. Items are instances of
    :class:VoucherType`.

    The :attr:`Journal.voucher_type
    <lino_xl.lib.ledger.models.Journal.voucher_type>` field points
    to an item of this.

    """

    required_roles = dd.login_required(LedgerStaff)
    verbose_name = _("Voucher type")
    verbose_name_plural = _("Voucher types")

    item_class = VoucherType
    max_length = 100

    @classmethod
    def get_for_model(self, model):
        """
        Return the :class:`VoucherType` for the given model.
        """
        for o in self.objects():
            if issubclass(o.model, model):
                return o

    @classmethod
    def get_for_table(self, table_class):
        """
        Return the :class:`VoucherType` for the given table.
        """
        for o in self.objects():
            if issubclass(o.table_class, table_class):
                return o

    # @classmethod
    # def add_item(cls, *args, **kwargs):
    #     return cls.add_item_instance(VoucherType(*args, **kwargs))


class TradeType(dd.Choice):
    """Base class for the choices of :class:`TradeTypes`.

    .. attribute:: dc

        The default booking direction.

    .. attribute:: price_field

        The name and label of the `price` field to be defined on the
        :class:`Product <lino.modlib.products.models.Product>`
        database model.

        With Lino Così you can define one price field per trade type.

    .. attribute:: partner_account_field

        The name and label of the :guilabel:`Partner account` field to
        be defined for this trade type on the :class:`SiteConfig
        <lino.modlib.system.models.SiteConfig>` database model.

    .. attribute:: base_account_field

        The name and label of the :guilabel:`Base account` field to
        be defined for this trade type on the :class:`SiteConfig
        <lino.modlib.system.models.SiteConfig>` database model.


    .. attribute:: vat_account_field

        The name and label of the :guilabel:`VAT account` field to be
        defined for this trade type on the :class:`SiteConfig
        <lino.modlib.system.models.SiteConfig>` database model.

    """
    price_field_name = None
    price_field_label = None
    partner_account_field_name = None
    partner_account_field_label = None
    base_account_field_name = None
    base_account_field_label = None
    vat_account_field_name = None
    vat_account_field_label = None
    dc = DEBIT

    def get_base_account(self):
        """Return the :class:`lino_xl.lib.accounts.models.Account` into which
        the **base amount** of any operation should be booked.

        """
        if self.base_account_field_name is None:
            return None
            # raise Exception("%s has no base_account_field_name!" % self)
        return getattr(settings.SITE.site_config,
                       self.base_account_field_name)

    def get_vat_account(self):
        """Return the :class:`Account <lino_xl.lib.accounts.models.Account>`
        into which the **VAT amount** of any operation should be
        booked.

        """
        if self.vat_account_field_name is None:
            return None
            # raise Exception("%s has no vat_account_field_name!" % self)
        return getattr(settings.SITE.site_config, self.vat_account_field_name)

    def get_partner_account(self):
        """Return the :class:`Account <lino_xl.lib.accounts.models.Account>`
        into which the **total amount** of any operation (base + VAT)
        should be booked.

        """
        if self.partner_account_field_name is None:
            return None
        return getattr(
            settings.SITE.site_config, self.partner_account_field_name)

    def get_product_base_account(self, product):
        """Return the :class:`Account <lino_xl.lib.accounts.models.Account>`
        into which the **base amount** of any operation should be
        booked.

        """
        if self.base_account_field_name is None:
            raise Exception("%s has no base_account_field_name" % self)
        return getattr(product, self.base_account_field_name) or \
            getattr(settings.SITE.site_config, self.base_account_field_name)

    def get_catalog_price(self, product):
        """Return the catalog price of the given product for operations with
        this trade type.

        """
        return getattr(product, self.price_field_name)


class TradeTypes(dd.ChoiceList):
    """A choicelist with the *trade types* defined for this application.

    The **trade type** is one of the basic properties of every ledger
    operation which involves an external partner.  Every partner
    movement belongs to one and only one trade type.

    The default configuration defines the following trade types:

    .. attribute:: sales

        A sale transaction is when you write an invoice to a customer
        and then expect the customer to pay it.

    .. attribute:: purchases

        A purchase transaction is when you get an invoice from a
        provider who expects you to pay it.


    .. attribute:: wages

        A wage transaction is when you write a payroll (declare the
        fact that you owe some wage to an employee) and later pay it
        (e.g. via a payment order).


    .. attribute:: clearings

        A clearing transaction is when an employee declares that he
        paid some invoice for you, and later you pay that money back
        to his account.

    """

    required_roles = dd.login_required(LedgerStaff)
    verbose_name = _("Trade type")
    verbose_name_plural = _("Trade types")
    item_class = TradeType
    help_text = _("The type of trade: usually either `sales` or `purchases`.")

TradeTypes.add_item('S', _("Sales"), 'sales', dc=CREDIT)
TradeTypes.add_item('P', _("Purchases"), 'purchases', dc=DEBIT)
TradeTypes.add_item('W', _("Wages"), 'wages', dc=DEBIT)
TradeTypes.add_item('C', _("Clearings"), 'clearings', dc=DEBIT)

# Note that :mod:`lino_xl.lib.sales.models` and/or
# :mod:`lino_xl.lib.ledger.models` (if installed) will modify
# `TradeTypes.sales` at module level so that the following
# `inject_vat_fields` will inject the required fields to
# system.SiteConfig and products.Product (if these are installed).


@dd.receiver(dd.pre_analyze)
def inject_tradetype_fields(sender, **kw):
    """This defines certain database fields related to your
    :class:`TradeTypes`.

    """
    for tt in TradeTypes.items():
        if tt.partner_account_field_name is not None:
            dd.inject_field(
                'system.SiteConfig',
                tt.partner_account_field_name,
                dd.ForeignKey(
                    'accounts.Account',
                    verbose_name=tt.partner_account_field_label,
                    related_name='configs_by_' + tt.partner_account_field_name,
                    blank=True, null=True))
        if tt.vat_account_field_name is not None:
            dd.inject_field('system.SiteConfig', tt.vat_account_field_name,
                            dd.ForeignKey(
                                'accounts.Account',
                                verbose_name=tt.vat_account_field_label,
                                related_name='configs_by_' +
                                tt.vat_account_field_name,
                                blank=True, null=True))
        if tt.base_account_field_name is not None:
            dd.inject_field('system.SiteConfig', tt.base_account_field_name,
                            dd.ForeignKey(
                                'accounts.Account',
                                verbose_name=tt.base_account_field_label,
                                related_name='configs_by_' +
                                tt.base_account_field_name,
                                blank=True, null=True))
            dd.inject_field('products.Product', tt.base_account_field_name,
                            dd.ForeignKey(
                                'accounts.Account',
                                verbose_name=tt.base_account_field_label,
                                related_name='products_by_' +
                                tt.base_account_field_name,
                                blank=True, null=True))
        if tt.price_field_name is not None:
            dd.inject_field('products.Product', tt.price_field_name,
                            dd.PriceField(verbose_name=tt.price_field_label,
                                          blank=True, null=True))


class VoucherState(dd.State):
    """Base class for items of :class:`VoucherStates`.
    """
    editable = False
    """
    Whether a voucher in this state is editable.
    """


class VoucherStates(dd.Workflow):
    """:class:`lino_xl.lib.ledger.VoucherStates` defines the list of
possible states of a voucher.

In a default configuration, vouchers can be :attr:`draft`,
:attr:`registered`, :attr:`cancelled` or :attr:`signed`.

.. attribute:: draft

    *Draft* vouchers can be modified but are not yet visible as movements
    in the ledger.

.. attribute:: registered

    *Registered* vouchers cannot be modified, but are visible as
    movements in the ledger.

.. attribute:: cancelled

    *Cancelled* is similar to *Draft*, except that you cannot edit the
    fields. This is used for invoices which have been sent, but the
    customer signaled that they doen't agree. Instead of writing a
    credit nota, you can decide to just cancel the invoice.

.. attribute:: signed

    The *Signed* state is similar to *registered*, but cannot usually be
    deregistered anymore. This state is not visible in the default
    configuration. In order to make it usable, you must define a custom
    workflow for :class:`lino_xl.lib.ledger.VoucherStates`.

    """

    item_class = VoucherState

    @classmethod
    def get_editable_states(cls):
        return [o for o in cls.objects() if o.editable]

add = VoucherStates.add_item
add('10', _("Draft"), 'draft', editable=True)
add('20', _("Registered"), 'registered')
add('30', _("Signed"), 'signed')
add('40', _("Cancelled"), 'cancelled')


@dd.receiver(dd.pre_analyze)
def setup_vat_workflow(sender=None, **kw):
    if False:
        VoucherStates.registered.add_transition(
            _("Register"), required_states='draft', icon_name='accept')
        VoucherStates.draft.add_transition(
            _("Deregister"), required_states="registered", icon_name='pencil')
    elif False:
        VoucherStates.registered.add_transition(
            # unichr(0x25c6),  # ◆
            _("Register"),
            help_text=_("Register"),
            required_states='draft')
        VoucherStates.draft.add_transition(
            _("Deregister"),
            # unichr(0x25c7),  # ◇
            help_text=_("Deregister"),
            required_roles=dd.login_required(LedgerStaff),
            required_states="registered")
    else:
        VoucherStates.registered.add_transition(
            # unichr(0x25c6),  # ◆
            # _("Register"),
            # help_text=_("Register"),
            required_states='draft')
        VoucherStates.draft.add_transition(
            # unichr(0x25c7),  # ◇
            # _("Deregister"),
            # help_text=_("Deregister"),
            required_roles=dd.login_required(LedgerStaff),
            required_states="registered cancelled")
        VoucherStates.cancelled.add_transition(
            # unichr(0x25c6),  # ◆
            # _("Cancel"),
            # help_text=_("Cancel"),
            required_states='draft')


