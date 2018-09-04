# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from builtins import str

from decimal import Decimal
ZERO = Decimal()

from django.db import models

from django.utils.text import format_lazy
from django.utils import translation

# from etgen.html import E, join_elems
from lino.modlib.gfks.fields import GenericForeignKeyIdField
from lino.core.gfks import GenericForeignKey, ContentType

from lino.modlib.users.mixins import UserPlan, My

# from lino_xl.lib.ledger.choicelists import VoucherTypes

from lino.api import dd, rt, _
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
from .mixins import Invoiceable
from .actions import (ToggleSelection, StartInvoicing,
                      StartInvoicingForJournal,
                      StartInvoicingForPartner, ExecutePlan,
                      ExecuteItem)


class SalesRule(dd.Model):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'SalesRule')
        verbose_name = _("Sales rule")
        verbose_name_plural = _("Sales rules")

    allow_cascaded_delete = 'partner'

    partner = dd.OneToOneField('contacts.Partner', primary_key=True)
    invoice_recipient = dd.ForeignKey(
        'contacts.Partner',
        verbose_name=_("Invoicing address"),
        related_name='salesrules_by_recipient',
        blank=True, null=True,
        help_text=_("Redirect to another partner all invoices which "
                    "should go to this partner."))
    paper_type = dd.ForeignKey(
        'sales.PaperType', null=True, blank=True)



class SalesRules(dd.Table):
    model = 'invoicing.SalesRule'
    required_roles = dd.login_required(LedgerStaff)
    detail_layout = dd.DetailLayout("""
    partner
    invoice_recipient
    paper_type
    """, window_size=(40, 'auto'))

class PartnersByInvoiceRecipient(SalesRules):
    help_text = _("Show partners having this as invoice recipient.")
    details_of_master_template = _("%(master)s used as invoice recipient")
    button_text = "♚"  # 265A
    master_key = 'invoice_recipient'
    column_names = "partner partner__id partner__address_column *"
    window_size = (80, 20)


dd.inject_action(
    'contacts.Partner',
    show_invoice_partners=dd.ShowSlaveTable(
        PartnersByInvoiceRecipient))



@dd.python_2_unicode_compatible
class Plan(UserPlan):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Plan')
        verbose_name = _("Invoicing plan")
        verbose_name_plural = _("Invoicing plans")

    journal = dd.ForeignKey('ledger.Journal', blank=True, null=True)
    max_date = models.DateField(
        _("Invoiceables until"), null=True, blank=True)
    partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)

    execute_plan = ExecutePlan()
    start_invoicing = StartInvoicing()

    @dd.chooser()
    def journal_choices(cls):
        vt = dd.plugins.invoicing.get_voucher_type()
        return rt.models.ledger.Journal.objects.filter(voucher_type=vt)

    def full_clean(self):
        if self.journal is None:
            vt = dd.plugins.invoicing.get_voucher_type()
            jnl_list = vt.get_journals()
            if len(jnl_list):
                self.journal = jnl_list[0]

    def get_invoiceables_for_plan(self, partner=None):
        for m in rt.models_by_base(Invoiceable):
            for obj in m.get_invoiceables_for_plan(self, partner):
                if obj.get_invoiceable_product(self) is not None:
                    yield obj

    def update_plan(self, ar):
        self.items.all().delete()
        self.fill_plan(ar)
        
    def fill_plan(self, ar):
        Item = rt.models.invoicing.Item
        collected = dict()
        for obj in self.get_invoiceables_for_plan():
            partner = obj.get_invoiceable_partner()
            if partner is None:
                raise Exception("{!r} has no invoice recipient".format(
                    obj))
            idate = obj.get_invoiceable_date()
            item = collected.get(partner.pk, None)
            if item is None:
                item = Item(plan=self, partner=partner)
                collected[partner.pk] = item
            if item.first_date is None:
                item.first_date = idate
            else:
                item.first_date = min(idate, item.first_date)
            if item.last_date is None:
                item.last_date = idate
            else:
                item.last_date = max(idate, item.last_date)
            if obj.amount:
                item.amount += obj.amount
            n = len(item.preview.splitlines())
            if n <= ItemsByPlan.row_height:
                if item.preview:
                    item.preview += '<br>\n'
                ctx = dict(
                    title=obj.get_invoiceable_title(),
                    amount=obj.amount,
                    currency=dd.plugins.ledger.currency_symbol)
                item.preview += "{title} ({amount} {currency})".format(
                    **ctx)
            elif n == ItemsByPlan.row_height + 1:
                item.preview += '...'
            item.number_of_invoiceables += 1
            item.save()


    toggle_selections = ToggleSelection()

    def __str__(self):
        # return "{0} {1}".format(self._meta.verbose_name, self.user)
        # return self._meta.verbose_name
        return str(self.user)


@dd.python_2_unicode_compatible
class Item(dd.Model):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Item')
        verbose_name = _("Invoicing suggestion")
        verbose_name_plural = _("Invoicing suggestions")

    plan = dd.ForeignKey('invoicing.Plan', related_name="items")
    partner = dd.ForeignKey('contacts.Partner')
    first_date = models.DateField(_("First date"))
    last_date = models.DateField(_("Last date"))
    amount = dd.PriceField(_("Amount"), default=ZERO)
    number_of_invoiceables = models.IntegerField(_("Number"), default=0)
    preview = models.TextField(_("Preview"), blank=True)
    selected = models.BooleanField(_("Selected"), default=True)
    invoice = dd.ForeignKey(
        dd.plugins.invoicing.voucher_model,
        verbose_name=_("Invoice"),
        null=True, blank=True,
        on_delete=models.SET_NULL)

    exec_item = ExecuteItem()

    def create_invoice(self,  ar):
        if self.plan.journal is None:
            raise Warning(_("No journal specified"))
        ITEM_MODEL = dd.resolve_model(dd.plugins.invoicing.item_model)
        M = ITEM_MODEL._meta.get_field('voucher').remote_field.model
        invoice = M(partner=self.partner, journal=self.plan.journal,
                    voucher_date=self.plan.today,
                    user=ar.get_user(),
                    entry_date=self.plan.today)
        lng = invoice.get_print_language()
        items = []
        with translation.override(lng):
            for ii in self.plan.get_invoiceables_for_plan(self.partner):
                pt = ii.get_invoiceable_payment_term()
                if pt:
                    invoice.payment_term = pt
                pt = ii.get_invoiceable_paper_type()
                if pt:
                    invoice.paper_type = pt
                for i in ii.get_wanted_items(
                        ar, invoice, self.plan, ITEM_MODEL):
                    items.append(i)

        if len(items) == 0:
            raise Warning(_("No invoiceables found for %s.") % self)
            # dd.logger.warning(
            #     _("No invoiceables found for %s.") % self.partner)
            # return

        invoice.full_clean()
        invoice.save()

        for i in items:
            i.voucher = invoice
            i.full_clean()
            i.save()

        self.invoice = invoice
        self.save()

        invoice.compute_totals()
        invoice.full_clean()
        invoice.save()
        invoice.register(ar)

        return invoice

    def __str__(self):
        return "{0} {1}".format(self.plan, self.partner)

class Plans(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = "invoicing.Plan"
    detail_layout = """user journal today max_date partner
    invoicing.ItemsByPlan
    """


class MyPlans(My, Plans):
    pass


class AllPlans(Plans):
    required_roles = dd.login_required(LedgerStaff)


class Items(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = "invoicing.Item"


class ItemsByPlan(Items):
    verbose_name_plural = _("Suggestions")
    master_key = 'plan'
    row_height = 2
    column_names = "selected partner preview amount invoice workflow_buttons *"


class InvoicingsByInvoiceable(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = dd.plugins.invoicing.item_model
    label = _("Invoicings")
    master_key = 'invoiceable'
    editable = False
    column_names = "voucher qty title description:20x1 #discount " \
                   "unit_price total_incl #total_base #total_vat *"


invoiceable_label = dd.plugins.invoicing.invoiceable_label



dd.inject_field(
    dd.plugins.invoicing.item_model,
    'invoiceable_type', dd.ForeignKey(
        ContentType,
        blank=True, null=True,
        verbose_name=format_lazy(u"{} {}",invoiceable_label, _('(type)'))))
dd.inject_field(
    dd.plugins.invoicing.item_model,
    'invoiceable_id', GenericForeignKeyIdField(
        'invoiceable_type',
        blank=True, null=True,
        verbose_name=format_lazy(u"{} {}",invoiceable_label, _('(object)'))))
dd.inject_field(
    dd.plugins.invoicing.item_model,
    'invoiceable', GenericForeignKey(
        'invoiceable_type', 'invoiceable_id',
        verbose_name=invoiceable_label))

# define a custom chooser because we want to see only invoiceable
# models when manually selecting an invoiceable_type:
@dd.chooser()
def invoiceable_type_choices(cls):
    return ContentType.objects.get_for_models(
        *rt.models_by_base(Invoiceable)).values()
dd.inject_action(
    dd.plugins.invoicing.item_model,
    invoiceable_type_choices=invoiceable_type_choices)


@dd.receiver(dd.pre_save, sender=dd.plugins.invoicing.item_model)
def item_pre_save_handler(sender=None, instance=None, **kwargs):
    """When the user sets `title` of an automatically generated invoice
    item to an empty string, then Lino restores the default value for
    both title and description

    """
    self = instance
    if self.invoiceable_id and not self.title:
        lng = self.voucher.get_print_language()
        # lng = self.voucher.partner.language or dd.get_default_language()
        with translation.override(lng):
            self.title = self.invoiceable.get_invoiceable_title(self.voucher)
            self.invoiceable.setup_invoice_item(self)


# def get_invoicing_voucher_type():
#     voucher_model = dd.resolve_model(dd.plugins.invoicing.voucher_model)
#     vt = VoucherTypes.get_for_model(voucher_model)


@dd.receiver(dd.pre_analyze)
def install_start_action(sender=None, **kwargs):
    vt = dd.plugins.invoicing.get_voucher_type()
    # vt = get_invoicing_voucher_type()
    vt.table_class.start_invoicing = StartInvoicingForJournal()

    rt.models.contacts.Partner.start_invoicing = StartInvoicingForPartner()
    

