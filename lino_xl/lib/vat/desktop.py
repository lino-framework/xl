# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Tables for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, rt, _

from lino.utils.xmlgen.html import E

from .mixins import VatDocument

from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal, PrintableByJournal
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
from lino_xl.lib.ledger.mixins import ItemsByVoucher

from .models import VatAccountInvoice


class VatRules(dd.Table):
    """The table of all :class:`lino_xl.lib.vat.models.VatRule` objects."""

    model = 'vat.VatRule'
    required_roles = dd.login_required(LedgerStaff)
    column_names = "seqno country trade_type vat_class vat_regime \
    #start_date #end_date rate can_edit vat_account vat_returnable_account *"
    hide_sums = True
    auto_fit_column_widths = True
    order_by = ['seqno']


class InvoiceDetail(dd.DetailLayout):
    """The detail layout used by :class:`Invoices`.

    """
    
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
    ItemsByInvoice:60 totals:20
    """, label=_("General"))

    ledger = dd.Panel("""
    journal accounting_period number narration
    ledger.MovementsByVoucher
    """, label=_("Ledger"))


class Invoices(PartnerVouchers):
    """The table of all
    :class:`VatAccountInvoice<lino_xl.lib.vat.models.VatAccountInvoice>`
    objects.

    """
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
    """Shows all invoices of a given journal (whose
    :attr:`voucher_type<lino_xl.lib.ledger.models.Journal.voucher_type>`
    must be :class:`lino_xl.lib.vat.models.VatAccountInvoice`)

    """
    params_layout = "partner state start_period end_period user"
    column_names = "number_with_year voucher_date due_date " \
        "partner " \
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
    column_names = "account title vat_class total_base total_vat total_incl"


class VouchersByPartner(dd.VirtualTable):
    """A :class:`lino.core.tables.VirtualTable` which shows all VatDocument
    vouchers by :class:`lino_xl.lib.contacts.models.Partner`. It has a
    customized slave summary.

    """
    required_roles = dd.login_required(LedgerUser)
    label = _("VAT vouchers")
    order_by = ["-entry_date", '-id']
    master = 'contacts.Partner'
    column_names = "entry_date voucher total_incl total_base total_vat"

    slave_grid_format = 'summary'

    @classmethod
    def get_data_rows(self, ar):
        obj = ar.master_instance
        rows = []
        if obj is not None:
            for M in rt.models_by_base(VatDocument):
                rows += list(M.objects.filter(partner=obj))

            def by_date(a, b):
                return cmp(b.entry_date, a.entry_date)

            rows.sort(by_date)
        return rows

    @dd.displayfield(_("Voucher"))
    def voucher(self, row, ar):
        return ar.obj2html(row)

    @dd.virtualfield('ledger.Voucher.entry_date')
    def entry_date(self, row, ar):
        return row.entry_date

    @dd.virtualfield('vat.VatAccountInvoice.total_incl')
    def total_incl(self, row, ar):
        return row.total_incl

    @dd.virtualfield('vat.VatAccountInvoice.total_base')
    def total_base(self, row, ar):
        return row.total_base

    @dd.virtualfield('vat.VatAccountInvoice.total_vat')
    def total_vat(self, row, ar):
        return row.total_vat

    @classmethod
    def get_slave_summary(self, obj, ar):

        elems = []
        sar = self.request(master_instance=obj)
        # elems += ["Partner:", unicode(ar.master_instance)]

        for voucher in sar:
            vc = voucher.get_mti_leaf()
            if vc and vc.state.name == "draft":
                elems += [ar.obj2html(vc), " "]

        vtypes = []
        for vt in VoucherTypes.items():
            if issubclass(vt.model, VatDocument):
                vtypes.append(vt)

        actions = []

        if not ar.get_user().user_type.readonly:
            for vt in vtypes:
                for jnl in vt.get_journals():
                    sar = vt.table_class.insert_action.request_from(
                        ar, master_instance=jnl,
                        known_values=dict(partner=obj))
                    btn = sar.ar2button(label=unicode(jnl), icon_name=None)
                    if len(actions):
                        actions.append(', ')
                    actions.append(btn)

        elems += [E.br(), _("Create voucher in journal"), " "] + actions
        return E.div(*elems)


