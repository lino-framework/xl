# -*- coding: UTF-8 -*-
# Copyright 2008-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.conf import settings
from django.db import models
from django.utils.text import format_lazy

from etgen.html import E

from lino.api import dd, rt, _, gettext
from lino.mixins.registrable import RegistrableState

from lino_xl.lib.ledger.utils import DEBIT, CREDIT
from .roles import LedgerStaff

class MissingAccount(object):
    def __init__(self, common_account):
        self.common_account = common_account

    def __str__(self):
        return _("No account pointing to {}").format(self.common_account)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, repr(self.common_account))


class JournalGroup(dd.Choice):
    menu_group = None
    # def __init__(self, value, text, name, menu_group=None, **kwargs):
    #     self.menu_group = dd.plugins.get(menu_group)
    #     super(JournalGroup, self).__init__(value, text, name, **kwargs)

class JournalGroups(dd.ChoiceList):
    item_class = JournalGroup
    verbose_name = _("Journal group")
    verbose_name_plural = _("Journal groups")
    required_roles = dd.login_required(LedgerStaff)

add = JournalGroups.add_item
add('10', _("Sales"), 'sales')
add('20', _("Purchases"), 'purchases')
add('30', _("Wages"), 'wages')
add('40', _("Financial"), 'financial')
# add('40', _("Money and banks"), 'money')
add('50', _("VAT"), 'vat')
add('60', _("Miscellaneous transactions"), 'misc')

if dd.is_installed("sales"):
    JournalGroups.sales.menu_group = dd.plugins.sales
    # JournalGroups.purchases.menu_group = dd.plugins.ledger


class PeriodStates(dd.Workflow):
    pass

add = PeriodStates.add_item
add('10', _("Open"), 'open')
add('20', _("Closed"), 'closed')


class CommonAccount(dd.Choice):
    show_values = True
    clearable = False
    needs_partner = False
    # sheet_item = ''  # filled by lino_xl.lib.sheets if installed
    _instance = None

    def __init__(self, value, text, name, clearable, **kwargs):
        # the class attribute `name` ís used as value
        super(CommonAccount, self).__init__(value, text, name, **kwargs)
        # self.sheet_item = CommonItems.get_by_name(actype)
        # self.clearable = clearable
        self.clearable = clearable
        self.needs_partner = clearable

    def create_object(self, **kwargs):
        kwargs.update(dd.str2kw('name', self.text))
        kwargs.update(clearable=self.clearable)
        kwargs.update(needs_partner=self.needs_partner)
        kwargs.update(common_account=self)
        # if dd.is_installed('sheets'):
        #     kwargs.update(sheet_item=self.sheet_item.get_object())
        # else:
        #     kwargs.pop('sheet_item', None)
        return rt.models.ledger.Account(
            ref=self.value, **kwargs)

    def set_object(self, obj):
        self._instance = obj

    def get_object(self):
        # return rt.models.ledger.Account.objects.get(ref=self.value)
        if self._instance is None:
            Account = rt.models.ledger.Account
            try:
                self._instance = Account.objects.get(common_account=self)
            except Account.DoesNotExist:
                self._instance = MissingAccount(self)
        return self._instance


class CommonAccounts(dd.ChoiceList):
    verbose_name = _("Common account")
    verbose_name_plural = _("Common accounts")
    item_class = CommonAccount
    column_names = 'value name text clearable db_object'
    required_roles = dd.login_required(LedgerStaff)

    # @dd.virtualfield(models.CharField(_("Sheet item"), max_length=20))
    # def sheet_item(cls, choice, ar):
    #     return choice.sheet_item

    @dd.virtualfield(dd.ForeignKey('ledger.Account'))
    def db_object(cls, choice, ar):
        obj = choice.get_object()
        if obj is None or isinstance(obj, MissingAccount):
            return None
        return obj

    @dd.virtualfield(models.BooleanField(_("Clearable")))
    def clearable(cls, choice, ar):
        return choice.clearable


add = CommonAccounts.add_item

add('1000', _("Net income (loss)"),   'net_income_loss', True)

add('4000', _("Customers"),   'customers', True)
add('4100', _("Suppliers"),   'suppliers', True)
add('4200', _("Employees"),   'employees', True)
add('4300', _("Pending Payment Orders"), 'pending_po', True)
add('4500', _("Tax Offices"), 'tax_offices', True)

add('4510', _("VAT due"), 'vat_due', False)
add('4520', _("VAT deductible"), 'vat_deductible', False)
add('4530', _("VAT returnable"), 'vat_returnable', False)
add('4513', _("VAT declared"), 'due_taxes', False)

add('4800', _("Internal clearings"), 'clearings', True)
add('4900', _("Waiting account"), 'waiting', True)

add('5500', _("BestBank"), 'best_bank', False)
add('5700', _("Cash"), 'cash', False)

add('6040', _("Purchase of goods"), 'purchase_of_goods', False)
add('6010', _("Purchase of services"), 'purchase_of_services', False)
add('6020', _("Purchase of investments"), 'purchase_of_investments', False)

add('6300', _("Wages"), 'wages', False)
add('6900', _("Net income"), 'net_income', False)

add('7000', _("Sales"), 'sales', False)
add('7900', _("Net loss"), 'net_loss', False)


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
            text = format_lazy(u"{} ({})",model._meta.verbose_name, value)
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
            # print(repr(e), e.__class__)
            if isinstance(e, GridElement):
                return e

    def get_journals(self, **kwargs):
        """Return a list of the :class:`Journal` objects that work on this
        voucher type.

        """
        kwargs.update(voucher_type=self)
        return rt.models.ledger.Journal.objects.filter(**kwargs)


class VoucherTypes(dd.ChoiceList):
    required_roles = dd.login_required(LedgerStaff)
    verbose_name = _("Voucher type")
    verbose_name_plural = _("Voucher types")
    column_names = "value name text model_name"

    item_class = VoucherType
    max_length = 100

    @classmethod
    def get_for_model(cls, model):
        """
        Return the :class:`VoucherType` for the given model.
        """
        return cls.find_unique(lambda i: issubclass(i.model, model))

    @classmethod
    def get_for_table(cls, table_class):
        """
        Return the :class:`VoucherType` for the given table.
        """
        # return cls.find_unique(lambda i: issubclass(i.table_class, table_class))
        return cls.find_unique(lambda i: i.table_class is table_class)

    @classmethod
    def find_unique(cls, func, default=None):

        """Find the unique item which matches the condition. Return default if
        no item or more than one item matches."""
        candidates = set()
        for o in cls.get_list_items():
            if func(o):
                candidates.add(o)
        if len(candidates) == 1:
            return candidates.pop()
        return default

    @dd.displayfield(_("Model"))
    def model_name(cls, vt, ar):
        return str(vt.model)


    # @classmethod
    # def add_item(cls, *args, **kwargs):
    #     return cls.add_item_instance(VoucherType(*args, **kwargs))


class TradeType(dd.Choice):
    price_field_name = None
    price_field_label = None
    main_account = None
    base_account = None
    base_account_field_name = None
    base_account_field_label = None
    invoice_account_field_name = None
    invoice_account_field_label = None
    dc = DEBIT

    def get_base_account(self):
        return self.base_account.get_object()

    def get_main_account(self):
        if self.main_account:
            return self.main_account.get_object()

    def get_product_base_account(self, product):
        if self.base_account_field_name is None:
            return self.base_account.get_object()
            # raise Exception("%s has no base_account_field_name" % self)
        return getattr(product, self.base_account_field_name, None) or \
            self.base_account.get_object()

    def get_partner_invoice_account(self, partner):
        if self.invoice_account_field_name is None:
            return None
        return getattr(partner, self.invoice_account_field_name, None)

    def get_catalog_price(self, product):
        return getattr(product, self.price_field_name)

    def get_allowed_accounts(self, **kw):
        kw[self.name + '_allowed'] = True
        return rt.models.ledger.Account.objects.filter(**kw)

def ca_fmt(ar, ca):
    if ar is None or ca is None:
        return ''
    elems = []
    obj = ca.get_object()
    if obj is None:
        elems.append(gettext("(undefined)"))
    else:
        # elems.append(ar.obj2html(obj))
        elems.append(str(obj))
    elems.append(u" ({})".format(ca))
    return E.div(*elems)

class TradeTypes(dd.ChoiceList):
    required_roles = dd.login_required(LedgerStaff)
    verbose_name = _("Trade type")
    verbose_name_plural = _("Trade types")
    item_class = TradeType
    help_text = _("The type of trade, e.g. 'sales' or 'purchases' or 'wages'.")
    column_names = "value name text main_account base_account "\
                   "product_account_field invoice_account_field"

    @dd.displayfield(_("Main account"))
    def main_account(cls, tt, ar):
        return ca_fmt(ar, tt.main_account)

    @dd.displayfield(_("Base account"))
    def base_account(cls, tt, ar):
        return ca_fmt(ar, tt.base_account)

    @dd.displayfield(_("Product account field"))
    def product_account_field(cls, tt, ar):
        if tt.base_account_field_name:
            return u"{} ({})".format(
                tt.base_account_field_label, tt.base_account_field_name)

    @dd.displayfield(_("Price field"))
    def product_price_field(cls, tt, ar):
        if tt.price_field_name:
            return u"{} ({})".format(
                tt.price_field_label, tt.price_field_name)

    @dd.displayfield(_("Invoice account field"))
    def invoice_account_field(cls, tt, ar):
        if tt.invoice_account_field_name:
            return u"{} ({})".format(
                tt.invoice_account_field_label, tt.invoice_account_field_name)

    # @dd.displayfield(_("Description"))
    # def description(cls, tt, ar):
    #     if ar is None:
    #         return ''
    #     elems = []
    #     if tt.base_account:
    #         elems += [gettext("Default base account"), ": "]
    #         elems += [str(tt.base_account)]
    #         elems += [" (", ar.obj2html(tt.get_base_account()), ")"]
    #     if tt.base_account_field_name:
    #         if len(elems): elems.append(", ")
    #         elems += [gettext("Product base account field"), ": "]
    #         elems += [str(tt.base_account_field_name)]
    #     if tt.invoice_account_field_name:
    #         if len(elems): elems.append(", ")
    #         elems += [gettext("Invoice account field"), ": "]
    #         elems += [str(tt.invoice_account_field_name)]
    #     return E.div(*elems)



TradeTypes.add_item(
    'S', _("Sales"), 'sales', dc=DEBIT,
    base_account=CommonAccounts.sales,
    main_account=CommonAccounts.customers)
TradeTypes.add_item(
    'P', _("Purchases"), 'purchases', dc=CREDIT,
    base_account=CommonAccounts.purchase_of_goods,
    main_account=CommonAccounts.suppliers,
    invoice_account_field_name='purchase_account',
    invoice_account_field_label=_("Purchase account")
)
TradeTypes.add_item(
    'W', _("Wages"), 'wages', dc=CREDIT,
    base_account=CommonAccounts.wages,
    main_account=CommonAccounts.employees)
TradeTypes.add_item(
    'T', _("Taxes"), 'taxes', dc=DEBIT,
    base_account=CommonAccounts.due_taxes,
    main_account=CommonAccounts.tax_offices)
TradeTypes.add_item(
    'C', _("Clearings"), 'clearings', dc=DEBIT,
    main_account=CommonAccounts.clearings)
TradeTypes.add_item(
    'B', _("Bank payment orders"), 'bank_po',
    dc=DEBIT, main_account=CommonAccounts.pending_po)

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
    # print(20200622, list([i.invoice_account_field_name for i in TradeTypes.items()]))
    for tt in TradeTypes.items():
        if tt.invoice_account_field_name is not None:
            dd.inject_field(
                'contacts.Partner', tt.invoice_account_field_name,
                dd.ForeignKey(
                    'ledger.Account',
                    verbose_name=tt.invoice_account_field_label,
                    on_delete=models.PROTECT,
                    related_name='partners_by_' + tt.invoice_account_field_name,
                    blank=True, null=True))
        if tt.base_account_field_name is not None:
            dd.inject_field(
                'products.Product', tt.base_account_field_name,
                dd.ForeignKey(
                    'ledger.Account',
                    verbose_name=tt.base_account_field_label,
                    on_delete=models.PROTECT,
                    related_name='products_by_' + tt.base_account_field_name,
                    blank=True, null=True))
        if tt.price_field_name is not None:
            dd.inject_field(
                'products.Product', tt.price_field_name,
                dd.PriceField(verbose_name=tt.price_field_label,
                              blank=True, null=True))


class VoucherState(RegistrableState):
    is_editable = False


class VoucherStates(dd.Workflow):
    item_class = VoucherState
    verbose_name = _("Voucher state")
    verbose_name_plural = _("Voucher states")
    column_names = "value name text is_editable"

    @classmethod
    def get_editable_states(cls):
        return [o for o in cls.objects() if o.is_editable]

    @dd.virtualfield(models.BooleanField(_("Editable")))
    def is_editable(cls, choice, ar):
        return choice.is_editable

add = VoucherStates.add_item
add('10', _("Draft"), 'draft', is_editable=True)
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
