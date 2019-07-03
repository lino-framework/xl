# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from django.db import models

from lino.api import dd, rt, _
from lino.core import actions
from etgen.html import E
from lino.utils.mldbc.mixins import BabelNamed
from lino.mixins.bleached import body_subject_to_elems
# from lino.mixins.periods import DateRange

from lino_xl.lib.sepa.mixins import Payable
from lino_xl.lib.ledger.mixins import Matching, SequencedVoucherItem
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.choicelists import TradeTypes
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal, PrintableByJournal
from lino_xl.lib.ledger.roles import LedgerStaff, LedgerUser
from .mixins import SalesDocument, ProductDocItem

TradeTypes.sales.update(
    price_field_name='sales_price',
    price_field_label=_("Sales price"),
    base_account_field_name='sales_account',
    base_account_field_label=_("Sales account"))


class PaperType(BabelNamed):

    templates_group = 'sales/VatProductInvoice'

    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'PaperType')
        verbose_name = _("Paper type")
        verbose_name_plural = _("Paper types")

    template = models.CharField(_("Template"), max_length=200, blank=True)

    @dd.chooser(simple_values=True)
    def template_choices(cls):
        bm = rt.models.printing.BuildMethods.get_system_default()
        return rt.find_template_config_files(
            bm.template_ext, cls.templates_group)


class PaperTypes(dd.Table):
    model = 'sales.PaperType'
    required_roles = dd.login_required(LedgerStaff)
    column_names = 'name template *'


class SalesDocuments(PartnerVouchers):
    pass

# class MakeCopy(dd.Action):
#     button_text = u"\u2042"  # ASTERISM (⁂)
    
#     label = _("Make copy")
#     show_in_workflow = True
#     show_in_bbar = False
#     copy_item_fields = set('product total_incl unit_price qty'.split())
    
#     parameters = dict(
#         partner=dd.ForeignKey('contacts.Partner'),
#         product=dd.ForeignKey('products.Product', blank=True),
#         subject=models.CharField(
#             _("Subject"), max_length=200, blank=True),
#         your_ref=models.CharField(
#             _("Your ref"), max_length=200, blank=True),
#         entry_date=models.DateField(_("Entry date")),
#         total_incl=dd.PriceField(_("Total incl VAT"), blank=True),
#     )
#     params_layout = """
#     entry_date partner
#     your_ref
#     subject
#     product total_incl
#     """

#     def action_param_defaults(self, ar, obj, **kw):
#         kw = super(MakeCopy, self).action_param_defaults(ar, obj, **kw)
#         kw.update(your_ref=obj.your_ref)
#         kw.update(subject=obj.subject)
#         kw.update(entry_date=obj.entry_date)
#         kw.update(partner=obj.partner)
#         # qs = obj.items.all()
#         # if qs.count():
#         #     kw.update(product=qs[0].product)
#         # kw.update(total_incl=obj.total_incl)
#         return kw

#     def run_from_ui(self, ar, **kw):
#         VoucherStates = rt.models.ledger.VoucherStates
#         obj = ar.selected_rows[0]
#         pv = ar.action_param_values
#         kw = dict(
#             journal=obj.journal,
#             user=ar.get_user(),
#             partner=pv.partner, entry_date=pv.entry_date,
#             subject=pv.subject,
#             your_ref=pv.your_ref)

#         new = obj.__class__(**kw)
#         new.fill_defaults()
#         new.full_clean()
#         new.save()
#         if pv.total_incl:
#             if not pv.product:
#                 qs = obj.items.all()
#                 if qs.count():
#                     pv.product = qs[0].product
#             item = new.add_voucher_item(
#                 total_incl=pv.total_incl, product=pv.product)
#             item.total_incl_changed(ar)
#             item.full_clean()
#             item.save()
#         else:
#             for olditem in obj.items.all():
#                 # ikw = dict()
#                 # for k in self.copy_item_fields:
#                 #     ikw[k] = getattr(olditem, k)
#                 ikw = { k: getattr(olditem, k)
#                         for k in self.copy_item_fields}
#                 item = new.add_voucher_item(**ikw)
#                 item.total_incl_changed(ar)
#                 item.full_clean()
#                 item.save()
            
#         new.full_clean()
#         new.register_voucher(ar)
#         new.state = VoucherStates.registered
#         new.save()
#         ar.goto_instance(new)
#         ar.success()




class VatProductInvoice(SalesDocument, Payable, Voucher, Matching):
    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'VatProductInvoice')
        verbose_name = _("Sales invoice")
        verbose_name_plural = _("Sales invoices")

    quick_search_fields = "partner__name subject"

    # show_items = dd.ShowSlaveTable('sales.ItemsByInvoice')

    # make_copy = MakeCopy()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(VatProductInvoice, cls).get_registrable_fields(site):
            yield f
        yield 'due_date'
        # yield 'order'

        yield 'voucher_date'
        yield 'entry_date'
        yield 'user'
        # yield 'item_vat'

    def get_print_items(self, ar):
        return self.print_items_table.request(self)

    @dd.virtualfield(dd.PriceField(_("Balance to pay")))
    def balance_to_pay(self, ar):
        Movement = rt.models.ledger.Movement
        qs = Movement.objects.filter(
            partner=self.get_partner(),
            cleared=False,
            match=self.get_match())
        return Movement.get_balance(not self.journal.dc, qs)

    @dd.virtualfield(dd.PriceField(_("Balance before")))
    def balance_before(self, ar):
        Movement = rt.models.ledger.Movement
        qs = Movement.objects.filter(
            partner=self.get_partner(),
            cleared=False,
            value_date__lte=self.entry_date)
        qs = qs.exclude(voucher=self)
        return Movement.get_balance(not self.journal.dc, qs)


class InvoiceDetail(dd.DetailLayout):
    main = "general more ledger"

    totals = dd.Panel("""
    total_base
    total_vat
    total_incl
    workflow_buttons
    """, label=_("Totals"))

    invoice_header = dd.Panel("""
    entry_date partner vat_regime
    #order subject your_ref match
    payment_term due_date:20 paper_type printed
    """, label=_("Header"))  # sales_remark

    general = dd.Panel("""
    invoice_header:60 totals:20
    ItemsByInvoice
    """, label=_("General"))

    more = dd.Panel("""
    id user language #project #item_vat
    intro
    """, label=_("More"))

    ledger = dd.Panel("""
    #voucher_date journal accounting_period number #narration
    ledger.MovementsByVoucher
    """, label=_("Ledger"))


class Invoices(SalesDocuments):
    model = 'sales.VatProductInvoice'
    required_roles = dd.login_required(LedgerUser)
    order_by = ["-id"]
    # order_by = ["journal", "accounting_period__year", "number"]
    column_names = "id entry_date partner total_incl user *"
    detail_layout = 'sales.InvoiceDetail'
    insert_layout = dd.InsertLayout("""
    partner entry_date
    subject
    """, window_size=(40, 'auto'))
    # parameters = dict(
    #     state=VoucherStates.field(blank=True),
    #     **SalesDocuments.parameters)

    # start_at_bottom = True

    # @classmethod
    # def get_request_queryset(cls, ar):
    #     qs = super(Invoices, cls).get_request_queryset(ar)
    #     pv = ar.param_values
    #     if pv.state:
    #         qs = qs.filter(state=pv.state)
    #     return qs


class InvoicesByJournal(Invoices, ByJournal):
    quick_search_fields = "partner subject"
    order_by = ["-accounting_period__year", "-number"]
    params_panel_hidden = True
    params_layout = "partner year state cleared"
    column_names = "number_with_year entry_date due_date " \
        "partner " \
        "total_incl subject:10 " \
        "workflow_buttons *"

class PrintableInvoicesByJournal(PrintableByJournal, Invoices):
    label = _("Sales invoice journal")


class DueInvoices(Invoices):
    label = _("Due invoices")
    order_by = ["due_date"]

    column_names = "due_date journal__ref number " \
        "partner " \
        "total_incl balance_before balance_to_pay *"

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(DueInvoices, cls).param_defaults(ar, **kw)
        kw.update(cleared=dd.YesNo.no)
        return kw


class InvoiceItem(ProductDocItem, SequencedVoucherItem):
    class Meta:
        app_label = 'sales'
        abstract = dd.is_abstract_model(__name__, 'InvoiceItem')
        verbose_name = _("Sales invoice item")
        verbose_name_plural = _("Sales invoice items")

    voucher = dd.ForeignKey(
        'sales.VatProductInvoice', related_name='items')
    title = models.CharField(_("Heading"), max_length=200, blank=True)
    # ship_ref = models.CharField(
    #     _("Shipment reference"), max_length=200, blank=True)
    # ship_date = models.DateField(_("Shipment date"), blank=True, null=True)


class InvoiceItemDetail(dd.DetailLayout):
    main = """
    seqno product discount
    unit_price qty total_base total_vat total_incl
    title
    description"""

    window_size = (80, 20)    
    


class InvoiceItems(dd.Table):
    """Shows all sales invoice items."""
    model = 'sales.InvoiceItem'
    required_roles = dd.login_required(LedgerStaff)
    auto_fit_column_widths = True
    # hidden_columns = "seqno description total_base total_vat"

    detail_layout = 'sales.InvoiceItemDetail'

    insert_layout = """
    product discount qty
    title
    """

    stay_in_grid = True


class ItemsByInvoice(InvoiceItems):
    label = _("Content")
    master_key = 'voucher'
    order_by = ["seqno"]
    required_roles = dd.login_required(LedgerUser)
    column_names = "product title discount unit_price qty total_incl *"



class ItemsByInvoicePrint(ItemsByInvoice):
    column_names = "description_print unit_price qty total_incl"
    include_qty_in_description = False

    @dd.displayfield(_("Description"))
    def description_print(cls, self, ar):
        title = self.title or str(self.product)
        elems = body_subject_to_elems(ar, title, self.description)
        # dd.logger.info("20160511a %s", cls)
        if cls.include_qty_in_description:
            if self.qty is not None and self.qty != 1:
                elems += [
                    " ",
                    _("({qty}*{unit_price}/{unit})").format(
                        qty=self.quantity,
                        unit=self.product.delivery_unit,
                        unit_price=self.unit_price)]
        e = E.div(*elems)
        # dd.logger.info("20160704d %s", tostring(e))
        return e
                

class ItemsByInvoicePrintNoQtyColumn(ItemsByInvoicePrint):
    column_names = "description_print total_incl"
    include_qty_in_description = True
    hide_sums = True


VatProductInvoice.print_items_table = ItemsByInvoicePrint


class InvoiceItemsByProduct(InvoiceItems):
    master_key = 'product'
    column_names = "voucher voucher__partner qty title \
description:20x1 discount unit_price total_incl total_base total_vat"
    editable = False
    # auto_fit_column_widths = True


class SignAction(actions.Action):
    label = "Sign"

    def run_from_ui(self, ar):

        def ok(ar):
            for row in ar.selected_rows:
                row.instance.user = ar.get_user()
                row.instance.save()
            ar.success(refresh=True)

        ar.confirm(
            ok, _("Going to sign %d documents as user %s. Are you sure?") % (
                len(ar.selected_rows),
                ar.get_user()))


class DocumentsToSign(Invoices):
    use_as_default_table = False
    filter = dict(user__isnull=True)
    # can_add = perms.never
    column_names = "number:4 #order entry_date " \
        "partner:10 " \
        "subject:10 total_incl total_base total_vat "
    # actions = Invoices.actions + [ SignAction() ]


class InvoicesByPartner(Invoices):
    # model = 'sales.VatProductInvoice'
    order_by = ["-entry_date", '-id']
    master_key = 'partner'
    column_names = "entry_date detail_link total_incl "\
                   "workflow_buttons *"
    # column_names = "entry_date journal__ref number total_incl "\
    #                "workflow_buttons *"


# class SalesByPerson(SalesDocuments):
    # column_names = "journal:4 number:4 date:8 " \
                   # "total_incl total_base total_vat *"
    # order_by = ["date"]
    # master_key = 'person'


VoucherTypes.add_item_lazy(InvoicesByJournal)


class ProductDetailMixin(dd.DetailLayout):
    sales = dd.Panel("""
    sales.InvoiceItemsByProduct
    """, label=dd.plugins.sales.verbose_name)
    

class PartnerDetailMixin(dd.DetailLayout):
    sales = dd.Panel("""
    salesrule__invoice_recipient vat_regime payment_term salesrule__paper_type
    sales.InvoicesByPartner
    """, label=dd.plugins.sales.verbose_name)


