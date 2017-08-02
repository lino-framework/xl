# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Choicelists for this plugin.

"""

from django.conf import settings
from django.utils.translation import string_concat

from lino.api import dd, rt, _

from lino_xl.lib.accounts.utils import DEBIT, CREDIT
from .roles import LedgerStaff


class JournalGroups(dd.ChoiceList):
    verbose_name = _("Journal group")
    verbose_name_plural = _("Journal groups")
    required_roles = dd.login_required(LedgerStaff)

add = JournalGroups.add_item
add('10', _("Sales"), 'sales')
add('20', _("Purchases"), 'purchases')
add('30', _("Wages"), 'wages')
add('40', _("Financial"), 'financial')
add('50', _("VAT"), 'vat')


class FiscalYear(dd.Choice):
    pass


class FiscalYears(dd.ChoiceList):

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
    pass

add = PeriodStates.add_item
add('10', _("Open"), 'open')
add('20', _("Closed"), 'closed')


class VoucherType(dd.Choice):
    # def __init__(self, model, table_class, text=None):
    def __init__(self, table_class, text=None):
        self.table_class = table_class
        model = dd.resolve_model(table_class.model)
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
    price_field_name = None
    price_field_label = None
    partner_account_field_name = None
    partner_account_field_label = None
    base_account_field_name = None
    base_account_field_label = None
    # vat_account_field_name = None
    # vat_account_field_label = None
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

    # def get_vat_account(self):
    #     """Return the :class:`Account <lino_xl.lib.accounts.models.Account>`
    #     into which the **VAT amount** of any operation should be
    #     booked.

    #     """
    #     if self.vat_account_field_name is None:
    #         return None
    #         # raise Exception("%s has no vat_account_field_name!" % self)
    #     return getattr(settings.SITE.site_config, self.vat_account_field_name)

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
    required_roles = dd.login_required(LedgerStaff)
    verbose_name = _("Trade type")
    verbose_name_plural = _("Trade types")
    item_class = TradeType
    help_text = _("The type of trade: usually either `sales` or `purchases`.")

TradeTypes.add_item('S', _("Sales"), 'sales', dc=CREDIT)
TradeTypes.add_item('P', _("Purchases"), 'purchases', dc=DEBIT)
TradeTypes.add_item('W', _("Wages"), 'wages', dc=DEBIT)
TradeTypes.add_item('T', _("Taxes"), 'taxes', dc=DEBIT)
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
        # if tt.vat_account_field_name is not None:
        #     # this field is no longer used except for backwards compat
        #     dd.inject_field('system.SiteConfig', tt.vat_account_field_name,
        #                     dd.ForeignKey(
        #                         'accounts.Account',
        #                         verbose_name=tt.vat_account_field_label,
        #                         related_name='configs_by_' +
        #                         tt.vat_account_field_name,
        #                         blank=True, null=True))
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
    editable = False


class VoucherStates(dd.Workflow):
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


