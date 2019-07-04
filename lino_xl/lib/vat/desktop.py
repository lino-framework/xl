# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, rt, _

# from etgen.html import E

from .mixins import VatDocument

from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal, PrintableByJournal
from lino_xl.lib.ledger.choicelists import TradeTypes
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
from lino_xl.lib.ledger.mixins import ItemsByVoucher
from lino_xl.lib.ledger.mixins import VouchersByPartnerBase

from .choicelists import VatRegimes, VatAreas


# class VatRules(dd.Table):

#     model = 'vat.VatRule'
#     required_roles = dd.login_required(LedgerStaff)
#     column_names = "seqno vat_area trade_type vat_class vat_regime \
#     #start_date #end_date rate can_edit \
#     vat_account vat_returnable vat_returnable_account *"
#     hide_sums = True
#     auto_fit_column_widths = True
#     order_by = ['seqno']


class InvoiceDetail(dd.DetailLayout):
    
    main = "general ledger"

    totals = """
    total_base
    total_vat
    total_incl
    workflow_buttons
    """

    general = dd.Panel("""
    id entry_date partner user
    due_date your_ref vat_regime #item_vat
    uploads.UploadsByController
    ItemsByInvoice:60 totals:20
    """, label=_("General"))

    ledger = dd.Panel("""
    journal accounting_period number narration
    ledger.MovementsByVoucher
    """, label=_("Ledger"))


class Invoices(PartnerVouchers):
    required_roles = dd.login_required(LedgerUser)
    model = 'vat.VatAccountInvoice'
    order_by = ["-id"]
    column_names = "entry_date id number_with_year partner total_incl user *"
    detail_layout = InvoiceDetail()
    insert_layout = """
    journal partner
    entry_date total_incl
    """
    # start_at_bottom = True


class InvoicesByJournal(Invoices, ByJournal):
    params_layout = "partner state start_period end_period user"
    column_names = "number_with_year entry_date due_date " \
        "your_ref partner " \
        "total_incl " \
        "total_base total_vat user workflow_buttons *"
                  #~ "ledger_remark:10 " \
    insert_layout = """
    partner
    entry_date total_incl
    """

class PrintableInvoicesByJournal(PrintableByJournal, Invoices):
    label = _("Purchase journal")

VoucherTypes.add_item_lazy(InvoicesByJournal)

class ItemsByInvoice(ItemsByVoucher):
    model = 'vat.InvoiceItem'
    display_mode = 'grid'
    column_names = "account title vat_class total_base total_vat total_incl"


class VouchersByPartner(VouchersByPartnerBase):
    label = _("VAT vouchers")
    column_names = "entry_date voucher total_incl total_base total_vat"
    _voucher_base = VatDocument

    @dd.virtualfield('vat.VatAccountInvoice.total_incl')
    def total_incl(self, row, ar):
        return row.total_incl

    @dd.virtualfield('vat.VatAccountInvoice.total_base')
    def total_base(self, row, ar):
        return row.total_base

    @dd.virtualfield('vat.VatAccountInvoice.total_vat')
    def total_vat(self, row, ar):
        return row.total_vat


class IntracomInvoices(PartnerVouchers):
    _trade_type = None
    editable = False
    model = VatDocument
    column_names = 'detail_link partner partner_vat_id vat_regime total_base total_vat total_incl'
    # order_by = ['entry_date', 'partner']
    # order_by = ['entry_date', 'id']
    # order_by = ['entry_date', 'number']
    order_by = ['number']
    hidden_elements = frozenset(
        """entry_date journal__trade_type journal number 
        journal__trade_type state user""".split())
    
    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        assert not kwargs
        fkw = dict()
        if cls._trade_type is not None:
            fkw.update(journal__trade_type=cls._trade_type)
        regimes = set([r for r in VatRegimes.get_list_items()
                       if r.vat_area == VatAreas.eu])
                       # if r.name.startswith('intracom')])
        # (VatRegimes.intracom, VatRegimes.intracom_supp)
        fkw.update(vat_regime__in=regimes)
        qs = super(IntracomInvoices, cls).get_request_queryset(ar, **fkw)
        # raise Exception("20170905 {}".format(qs.query))
        return qs

    @dd.virtualfield(dd.ForeignKey('contacts.Partner'))
    def partner(cls, obj, ar=None):
        return obj.partner

    @dd.virtualfield('contacts.Partner.vat_id')
    def partner_vat_id(cls, obj, ar=None):
        return obj.partner.vat_id

dd.update_field(IntracomInvoices, 'detail_link', verbose_name=_("Invoice"))
    
class IntracomSales(IntracomInvoices):
    _trade_type = TradeTypes.sales
    label = _("Intra-Community sales")

class IntracomPurchases(IntracomInvoices):
    _trade_type = TradeTypes.purchases
    label = _("Intra-Community purchases")
    
