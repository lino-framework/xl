# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
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


"""Actors for `lino_xl.lib.vatless`.



"""

from __future__ import unicode_literals

from lino.api import dd, rt, _

from lino.utils.xmlgen.html import E

from lino_xl.lib.ledger.mixins import PartnerRelated
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal

from .models import AccountInvoice


class InvoiceItems(dd.Table):
    model = 'vatless.InvoiceItem'
    # auto_fit_column_widths = True
    order_by = ['voucher', "seqno"]


class ItemsByInvoice(InvoiceItems):
    """This is the "content" part of an invoice.

    """
    column_names = "project account amount title move_buttons *"
    master_key = 'voucher'
    order_by = ["seqno"]


class ItemsByProjectInvoice(ItemsByInvoice):
    """Like :class:`ItemsByInvoice`, but in a project invoice we don't
    want to have a project column per item.

    """
    column_names = "account amount title move_buttons *"


class InvoiceDetail(dd.DetailLayout):
    main = "general ledger"

    general = dd.Panel("""
    journal number entry_date voucher_date accounting_period workflow_buttons
    partner payment_term due_date bank_account
    your_ref narration amount
    ItemsByInvoice
    """, label=_("General"))

    ledger = dd.Panel("""
    match state user id
    ledger.MovementsByVoucher
    """, label=_("Ledger"))


class ProjectInvoiceDetail(InvoiceDetail):
    general = dd.Panel("""
    journal number entry_date voucher_date accounting_period workflow_buttons
    project narration
    partner your_ref
    payment_term due_date bank_account amount
    ItemsByProjectInvoice
    """, label=_("General"))


class Invoices(PartnerVouchers):
    model = 'vatless.AccountInvoice'
    order_by = ["-id"]
    # parameters = dict(
    #     state=VoucherStates.field(blank=True),
    #     **PartnerVouchers.parameters)
    # params_layout = "project partner state journal year"
    # params_panel_hidden = True
    column_names = "entry_date id number partner amount user *"
    detail_layout = InvoiceDetail()
    insert_layout = """
    journal
    partner
    entry_date
    """
    # start_at_bottom = True

    # @classmethod
    # def get_request_queryset(cls, ar):
    #     qs = super(Invoices, cls).get_request_queryset(ar)
    #     pv = ar.param_values
    #     if pv.state:
    #         qs = qs.filter(state=pv.state)
    #     return qs

    # @classmethod
    # def unused_param_defaults(cls, ar, **kw):
    #     kw = super(Invoices, cls).param_defaults(ar, **kw)
    #     kw.update(pyear=FiscalYears.from_date(settings.SITE.today()))
    #     return kw


class InvoicesByJournal(ByJournal, Invoices):
    """Shows all simple invoices of a given journal (whose
    :attr:`Journal.voucher_type` must be
    :class:`lino_xl.lib.sales.models.AccountInvoice`).

    """
    params_layout = "partner state year"
    column_names = "number entry_date " \
        "partner amount due_date user workflow_buttons *"
    insert_layout = """
    partner
    entry_date
    """
    order_by = ["-id"]


class ProjectInvoicesByJournal(InvoicesByJournal):
    column_names = "number entry_date " \
        "project partner amount due_date user workflow_buttons *"
    insert_layout = """
    project
    partner
    entry_date
    """
    detail_layout = ProjectInvoiceDetail()
    

VoucherTypes.add_item(
    AccountInvoice, InvoicesByJournal, _("Invoices"))
VoucherTypes.add_item(
    AccountInvoice, ProjectInvoicesByJournal, _("Project invoices"))


class VouchersByPartner(dd.VirtualTable):
    """Shows all ledger vouchers of a given partner.
    
    This is a :class:`lino.core.tables.VirtualTable` with a customized
    slave summary.

    """
    label = _("Partner vouchers")
    order_by = ["-date", '-id']
    master = 'contacts.Partner'
    slave_grid_format = 'summary'

    column_names = "date voucher amount state"
    _master_field_name = 'partner'

    @classmethod
    def get_data_rows(self, ar):
        obj = ar.master_instance
        rows = []
        if obj is not None:
            flt = {self._master_field_name: obj}
            for M in rt.models_by_base(AccountInvoice):
                rows += list(M.objects.filter(**flt))

            def by_date(a, b):
                return cmp(b.entry_date, a.entry_date)

            rows.sort(by_date)
        return rows

    @dd.displayfield(_("Voucher"))
    def voucher(self, row, ar):
        return ar.obj2html(row)

    # if dd.plugins.ledger.project_model:
    #     @dd.virtualfield('ledger.Movement.project')
    #     def project(self, row, ar):
    #         return row.project

    @dd.virtualfield('ledger.Movement.partner')
    def partner(self, row, ar):
        return row.partner

    @dd.virtualfield('ledger.Voucher.entry_date')
    def date(self, row, ar):
        return row.entry_date

    @dd.virtualfield('ledger.Voucher.state')
    def state(self, row, ar):
        return row.state

    @dd.virtualfield('vatless.AccountInvoice.amount')
    def amount(self, row, ar):
        return row.amount

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
            if issubclass(vt.model, PartnerRelated):
                vtypes.append(vt)

        actions = []

        def add_action(btn):
            if btn is None:
                return False
            actions.append(btn)
            return True

        if not ar.get_user().user_type.readonly:
            flt = {self._master_field_name: obj}
            for vt in vtypes:
                for jnl in vt.get_journals():
                    sar = vt.table_class.insert_action.request_from(
                        ar, master_instance=jnl,
                        known_values=flt)
                    btn = sar.ar2button(label=unicode(jnl), icon_name=None)
                    if len(actions):
                        actions.append(', ')
                    actions.append(btn)

            elems += [E.br(), _("Create voucher in journal"), " "] + actions
        return E.div(*elems)


