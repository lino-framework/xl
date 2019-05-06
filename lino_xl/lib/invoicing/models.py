# -*- coding: UTF-8 -*-
# Copyright 2016-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from builtins import str

from django.db import models
from django.conf import settings
from django.utils.text import format_lazy
from django.utils import translation

# from etgen.html import E, join_elems
from lino.core.gfks import GenericForeignKey, ContentType
from lino.modlib.gfks.fields import GenericForeignKeyIdField
# from lino.core.gfks import gfk2lookup
from lino.utils.mldbc.mixins import BabelDesignated

from lino.modlib.users.mixins import UserPlan, My

# from lino_xl.lib.ledger.choicelists import VoucherTypes

from lino.mixins import Sequenced
from lino.utils import ONE_DAY
from lino.api import dd, rt, _
from lino_xl.lib.ledger.utils import ZERO
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff

from .mixins import InvoiceGenerator
# from .choicelists import InvoicingCycles
# from .choicelists import InvoicingDepartments
from .actions import (ToggleSelection, StartInvoicing,
                      # StartInvoicingByArea,
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
        blank=True, null=True)
    paper_type = dd.ForeignKey(
        'sales.PaperType', null=True, blank=True)

@dd.receiver(dd.post_save, sender='contacts.Partner')
def create_salesrule(sender, instance, created, **kwargs):
    if created and not settings.SITE.loading_from_dump:
        if not hasattr(instance, 'salesrule'):
            rt.models.invoicing.SalesRule.objects.create(partner=instance)



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


class Tariff(BabelDesignated):

    class Meta(object):
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Tariff')
        verbose_name = _("Flatrate")
        verbose_name_plural = _("Flatrates")

    # allow_cascaded_delete = 'product'

    # product = dd.OneToOneField('products.Product', primary_key=True)
    
    number_of_events = models.IntegerField(
        _("Number of events"), blank=True, null=True,
        help_text=_("Number of events paid per invoicing."))

    min_asset = models.IntegerField(
        _("Minimum threshold"), blank=True, null=True,
        help_text=_("Minimum quantity to pay in advance."))

    max_asset = models.IntegerField(
        _("Maximum threshold"), blank=True, null=True, 
        help_text=_("Maximum quantity to pay per period."))

    # invoicing_cycle = InvoicingCycles.field(default="once")

# @dd.receiver(dd.post_save, sender='products.Product')
# def create_tariff(sender, instance, created, **kwargs):
#     if created and not settings.SITE.loading_from_dump:
#         if not hasattr(instance, 'tariff'):
#             rt.models.invoicing.Tariff.objects.create(product=instance)


class Tariffs(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = "invoicing.Tariff"
    column_names = "designation number_of_events min_asset max_asset *"
    order_by = ['designation']


# @dd.python_2_unicode_compatible
class Area(BabelDesignated, Sequenced):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Area')
        verbose_name = _("Invoicing area")
        verbose_name_plural = _("Invoicing areas")

    # designation = dd.CharField(max_length=100)
    journal = dd.ForeignKey('ledger.Journal', blank=True, null=True)

    # start_invoicing = StartInvoicingForArea()

    # def __str__(self):
    #     return str(self.designation)

    @dd.chooser()
    def journal_choices(cls):
        vt = dd.plugins.invoicing.get_voucher_type()
        return rt.models.ledger.Journal.objects.filter(voucher_type=vt)

    def full_clean(self):
        if self.journal is None:
            vt = dd.plugins.invoicing.get_voucher_type()
            self.journal = vt.get_journals().first()

        # if not self.designation:
        #     self.designation = str(self.journal)
        super(Area, self).full_clean()


class Areas(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = "invoicing.Area"
    column_names = "seqno designation journal *"



@dd.python_2_unicode_compatible
class Plan(UserPlan):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Plan')
        verbose_name = _("Invoicing plan")
        verbose_name_plural = _("Invoicing plans")

    area = dd.ForeignKey('invoicing.Area', blank=True)
    min_date = models.DateField(
        _("Invoiceables from"), null=True, blank=True)
    max_date = models.DateField(
        _("until"), null=True, blank=True)
    partner = dd.ForeignKey('contacts.Partner', blank=True, null=True)

    execute_plan = ExecutePlan()
    start_plan = StartInvoicing()

    def full_clean(self):
        if self.area_id is None:
            self.area = rt.models.invoicing.Area.objects.first()
        super(Plan, self).full_clean()

    def get_max_date(self):
        if self.max_date:
            return self.max_date
        return self.today - ONE_DAY
    
    def get_generators_for_plan(self, partner=None):
        for m in rt.models_by_base(InvoiceGenerator):
            for obj in m.get_generators_for_plan(self, partner):
                # if obj.get_invoiceable_product(self) is not None:
                yield obj

    def reset_plan(self):
        self.items.all().delete()
        
    def run_update_plan(self, ar):
        self.reset_plan()
        self.fill_plan(ar)
        
    def fill_plan(self, ar):
        self.full_clean()
        Item = rt.models.invoicing.Item
        collected = dict()
        # dd.logger.info("20181114 a")
        max_date = self.get_max_date()

        for ig in self.get_generators_for_plan():
            partner = ig.get_invoiceable_partner()
            if partner is None:
                continue
                # raise Exception("{!r} has no invoice recipient".format(
                #     ig))
            if hasattr(partner, 'salesrule'):
                partner = partner.salesrule.invoice_recipient or partner

            invoice = self.create_invoice(
                partner=partner, user=ar.get_user())
        
            # dd.logger.info("20181114 b", obj)
            info = ig.compute_invoicing_info(max_date)
            # if not info.invoiceable_product:
            #     continue
            
            invoice_items = list(ig.get_invoice_items(info, invoice, ar))
            if len(invoice_items) == 0:
                # dd.logger.debug("20181126 no invoice items for %s", ig)
                continue

            if ig.allow_group_invoices():
                item = collected.get(partner.pk, None)
                if item is None:
                    item = Item(plan=self, partner=partner)
                    collected[partner.pk] = item
            else:
                item = Item(plan=self, partner=partner, generator=ig)
                # collected[obj] = item
                
                # gfk = self._meta.get_field('owner')
                # kwargs = gfk2lookup(gfk, self, **kwargs)
                # return model.objects.filter(**kwargs)

            # for ie in info.used_events:
            # # for ie in obj.get_invoiceable_events(
            # #         self.today, self.max_date):
            #     idate = ig.get_invoiceable_event_date(ie)
            #     if idate is None:
            #         dd.logger.info("20181113 idate is None")
            #         continue
            #     if item.first_date is None:
            #         item.first_date = idate
            #     else:
            #         item.first_date = min(idate, item.first_date)
            #     if item.last_date is None:
            #         item.last_date = idate
            #     else:
            #         item.last_date = max(idate, item.last_date)
            #     amount = ig.get_invoiceable_amount(ie)
            #     if amount:
            #         item.amount += amount
            # # if not item.amount:
            # #     dd.logger.info("20181113 amount is 0")
            # #     continue
            # n = len(item.preview.splitlines())
            # if n <= ItemsByPlan.row_height:
            #     if item.preview:
            #         item.preview += '<br>\n'
            #     ctx = dict(
            #         title=obj.get_invoiceable_title(),
            #         amount=item.amount,
            #         currency=dd.plugins.ledger.currency_symbol)
            #     item.preview += "{title} ({amount} {currency})".format(
            #         **ctx)
            # elif n == ItemsByPlan.row_height + 1:
            #     item.preview += '...'


            item.preview = "" # _("{} items").format(len(invoice_items))
            total_amount = ZERO
            for n, i in enumerate(invoice_items):
                i.discount_changed()
                total_amount += i.get_amount() or ZERO
                # item.preview += "<br>\n"
                # ctx = dict(
                #     title=i.title or i.product,
                #     amount=i.get_amount() or ZERO,
                #     currency=dd.plugins.ledger.currency_symbol)
                # item.preview += "{title} ({amount} {currency})".format(
                #     **ctx)

                if n < ItemsByPlan.row_height:
                    if item.preview:
                        item.preview += '<br>\n'
                    ctx = dict(
                        title=i.title or i.product,
                        amount=i.get_amount() or ZERO,
                        currency=dd.plugins.ledger.currency_symbol)
                    item.preview += "{title} ({amount} {currency})".format(
                        **ctx)
                elif n == ItemsByPlan.row_height:
                    item.preview += '...'
                
                
            item.amount = total_amount
            # item.number_of_invoiceables += 1
            item.full_clean()
            item.save()

    def create_invoice(self, **kwargs):
        # ITEM_MODEL = dd.plugins.invoicing.item_model
        M = dd.plugins.invoicing.voucher_model
        # M = ITEM_MODEL._meta.get_field('voucher').remote_field.model
        kwargs.update(
            journal=self.area.journal,
            entry_date=self.today,
            invoicing_min_date=self.min_date,
            invoicing_max_date=self.get_max_date())
        invoice = M(**kwargs)
        invoice.fill_defaults()
        return invoice
        

    toggle_selections = ToggleSelection()

    def __str__(self):
        # return "{0} {1}".format(self._meta.verbose_name, self.user)
        # return self._meta.verbose_name
        return str(self.user)

generator_label = _("Generator")


@dd.python_2_unicode_compatible
class Item(dd.Model):
    class Meta:
        app_label = 'invoicing'
        abstract = dd.is_abstract_model(__name__, 'Item')
        verbose_name = _("Invoicing suggestion")
        verbose_name_plural = _("Invoicing suggestions")

    plan = dd.ForeignKey('invoicing.Plan', related_name="items")
    partner = dd.ForeignKey('contacts.Partner')

    generator_type = dd.ForeignKey(
        ContentType,
        editable=True,
        blank=True, null=True,
        verbose_name=format_lazy(u"{} {}", generator_label, _('(type)')))
    generator_id = GenericForeignKeyIdField(
        generator_type,
        editable=True,
        blank=True, null=True,
        verbose_name=format_lazy(u"{} {}", generator_label, _('(object)')))
    generator = GenericForeignKey(
        'generator_type', 'generator_id',
        verbose_name=generator_label)

    
    # first_date = models.DateField(_("First date"))
    # last_date = models.DateField(_("Last date"))
    amount = dd.PriceField(_("Amount"), default=ZERO)
    # number_of_invoiceables = models.IntegerField(_("Number"), default=0)
    preview = models.TextField(_("Preview"), blank=True)
    selected = models.BooleanField(_("Selected"), default=True)
    invoice = dd.ForeignKey(
        dd.plugins.invoicing.voucher_model,
        verbose_name=_("Invoice"),
        null=True, blank=True,
        on_delete=models.SET_NULL)

    exec_item = ExecuteItem()

    @dd.displayfield(_("Invoice"))
    def invoice_button(self, ar):
        if ar is not None:
            if self.invoice_id:
                return self.invoice.obj2href(ar)
            ba = ar.actor.get_action_by_name('exec_item')
            if ar.actor.get_row_permission(self, ar, None, ba):
                return ar.action_button(ba, self)
        return ''
    
    def create_invoice(self,  ar):
        if self.plan.area_id is None:
            raise Warning(_("No area specified"))
        if self.plan.area.journal is None:
            raise Warning(_("No journal configured for {}").format(self.plan.area))
        invoice = self.plan.create_invoice(
            partner=self.partner, user=ar.get_user())
        lng = invoice.get_print_language()
        items = []
        max_date = self.plan.get_max_date()
        with translation.override(lng):
            if self.generator:
                generators = [self.generator]
            else:
                generators = [
                    ig for ig in self.plan.get_generators_for_plan(
                        self.partner) if ig.allow_group_invoices()]
            for ig in generators:
                info = ig.compute_invoicing_info(max_date)
                pt = ig.get_invoiceable_payment_term()
                if pt:
                    invoice.payment_term = pt
                pt = ig.get_invoiceable_paper_type()
                if pt:
                    invoice.paper_type = pt
                    
                # for i in ig.get_invoice_items(info, ITEM_MODEL, ar):
                for i in ig.get_invoice_items(info, invoice, ar):
                    # kwargs.update(voucher=invoice)
                    # i = ITEM_MODEL(**kwargs)
                    # if 'amount' in kwargs:
                    #     i.set_amount(ar, kwargs['amount'])
                    # amount = kwargs.get('amount', ZERO)
                    # if amount:
                    #     i.set_amount(ar, amount)
                    items.append((ig, i))

        if len(items) == 0:
            # neither invoice nor items are saved
            raise Warning(_("No invoiceables found for %s.") % self)
            # dd.logger.warning(
            #     _("No invoiceables found for %s.") % self.partner)
            # return

        invoice.full_clean()
        invoice.save()

        for ig, i in items:
            # assign voucher after it has been saved
            i.voucher = invoice
            ig.setup_invoice_item(i)
            # if not i.title:
            #     i.title = ig.get_invoiceable_title(invoice)
            # compute the sales_price and amounts, but don't change
            # title and description
            
            # title = i.title
            # i.product_changed()  
            i.discount_changed()
            # i.title = title
            i.full_clean()
            i.save()

        self.invoice = invoice
        self.full_clean()
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
    detail_layout = """user area today min_date max_date partner
    invoicing.ItemsByPlan
    """


class MyPlans(My, Plans):
    pass

# class PlansByArea(Plans):
#     master_key = 'area'
#     start_invoicing = StartInvoicingByArea()

class AllPlans(Plans):
    required_roles = dd.login_required(LedgerStaff)


class Items(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = "invoicing.Item"


class ItemsByPlan(Items):
    verbose_name_plural = _("Suggestions")
    master_key = 'plan'
    row_height = 2
    column_names = "selected partner preview amount invoice_button *"


class InvoicingsByGenerator(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = dd.plugins.invoicing.item_model
    label = _("Invoicings")
    master_key = 'invoiceable'
    editable = False
    column_names = "voucher qty title description:20x1 #discount " \
                   "unit_price total_incl #total_base #total_vat *"


invoiceable_label = dd.plugins.invoicing.invoiceable_label


dd.inject_field(
    'products.Product', 'tariff', dd.ForeignKey(
        'invoicing.Tariff', blank=True, null=True))

dd.inject_field(
    dd.plugins.invoicing.voucher_model, 'invoicing_min_date', dd.DateField(
        _("Invoiceables from"), blank=True, null=True))
dd.inject_field(
    dd.plugins.invoicing.voucher_model, 'invoicing_max_date', dd.DateField(
        _("until"), blank=True, null=True))

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

# dd.inject_field(
#     dd.plugins.invoicing.item_model,
#     'item_no', models.IntegerField(_("Iten no."))

# define a custom chooser because we want to see only invoiceable
# models when manually selecting an invoiceable_type:
@dd.chooser()
def invoiceable_type_choices(cls):
    return ContentType.objects.get_for_models(
        *rt.models_by_base(InvoiceGenerator)).values()
dd.inject_action(
    dd.plugins.invoicing.item_model,
    invoiceable_type_choices=invoiceable_type_choices)


# 20181115 : note this feature doesn't work when a generator creates
# more than one item because it would now require an additional field
# item_no per invoice item.
# @dd.receiver(dd.pre_save, sender=dd.plugins.invoicing.item_model)
# def item_pre_save_handler(sender=None, instance=None, **kwargs):
#     """
#     When the user sets `title` of an automatically generated invoice
#     item to an empty string, then Lino restores the default value for
#     title and description
#     """
#     self = instance
#     if self.invoiceable_id and not self.title:
#         lng = self.voucher.get_print_language()
#         # lng = self.voucher.partner.language or dd.get_default_language()
#         with translation.override(lng):
#             self.title = self.invoiceable.get_invoiceable_title(self.voucher)
#             self.invoiceable.setup_invoice_item(self)


# def get_invoicing_voucher_type():
#     voucher_model = dd.resolve_model(dd.plugins.invoicing.voucher_model)
#     vt = VoucherTypes.get_for_model(voucher_model)


@dd.receiver(dd.pre_analyze)
def install_start_action(sender=None, **kwargs):
    # vt = dd.plugins.invoicing.get_voucher_type()
    # vt.table_class.start_invoicing = StartInvoicingForJournal()

    rt.models.contacts.Partner.start_invoicing = StartInvoicingForPartner()
    

