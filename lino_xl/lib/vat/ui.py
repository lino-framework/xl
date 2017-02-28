# Copyright 2012-2015 Luc Saffre
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


"""Tables for `lino_xl.lib.vat`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, rt, _

from lino.utils.xmlgen.html import E

from .mixins import VatDocument

from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff

from .models import VatAccountInvoice


class VatRules(dd.Table):
    """The table of all :class:`lino_xl.lib.vat.models.VatRule` objects."""

    model = 'vat.VatRule'
    required_roles = dd.login_required(LedgerStaff)
    column_names = "seqno country vat_class vat_regime \
    start_date end_date rate can_edit *"
    hide_sums = True
    auto_fit_column_widths = True


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
    id voucher_date partner user
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
    column_names = "voucher_date id number partner total_incl user *"
    detail_layout = InvoiceDetail()
    insert_layout = """
    journal partner
    voucher_date total_incl
    """
    # start_at_bottom = True


class InvoicesByJournal(Invoices, ByJournal):
    """Shows all invoices of a given journal (whose
    :attr:`voucher_type<lino_xl.lib.ledger.models.Journal.voucher_type>`
    must be :class:`lino_xl.lib.vat.models.VatAccountInvoice`)

    """
    params_layout = "partner state year"
    column_names = "number voucher_date due_date " \
        "partner " \
        "total_incl " \
        "total_base total_vat user workflow_buttons *"
                  #~ "ledger_remark:10 " \
    insert_layout = """
    partner
    voucher_date total_incl
    """


VoucherTypes.add_item(VatAccountInvoice, InvoicesByJournal)


class ItemsByInvoice(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = 'vat.InvoiceItem'
    column_names = "account title vat_class total_base total_vat total_incl"
    master_key = 'voucher'
    order_by = ["seqno"]
    auto_fit_column_widths = True


class VouchersByPartner(dd.VirtualTable):
    """A :class:`lino.core.tables.VirtualTable` which shows all VatDocument
    vouchers by :class:`lino_xl.lib.contacts.models.Partner`. It has a
    customized slave summary.

    """
    required_roles = dd.login_required(LedgerUser)
    label = _("VAT vouchers")
    order_by = ["-voucher_date", '-id']
    master = 'contacts.Partner'
    column_names = "voucher_date voucher total_incl total_base total_vat"

    slave_grid_format = 'summary'

    @classmethod
    def get_data_rows(self, ar):
        obj = ar.master_instance
        rows = []
        if obj is not None:
            for M in rt.models_by_base(VatDocument):
                rows += list(M.objects.filter(partner=obj))

            def by_date(a, b):
                return cmp(b.voucher_date, a.voucher_date)

            rows.sort(by_date)
        return rows

    @dd.displayfield(_("Voucher"))
    def voucher(self, row, ar):
        return ar.obj2html(row)

    @dd.virtualfield('ledger.Voucher.voucher_date')
    def voucher_date(self, row, ar):
        return row.voucher_date

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

        if not ar.get_user().profile.readonly:
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


