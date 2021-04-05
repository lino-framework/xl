# -*- coding: UTF-8 -*-
# Copyright 2015-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _

from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal
from lino_xl.lib.ledger.mixins import ItemsByVoucher

# from .models import AccountInvoice


# class InvoiceItems(dd.Table):
#     model = 'vatless.InvoiceItem'
#     # auto_fit_column_widths = True
#     order_by = ['voucher', "seqno"]


class ItemsByInvoice(ItemsByVoucher):
    """This is the "content" part of an invoice.

    """
    model = 'vatless.InvoiceItem'
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
    column_names = "entry_date id number_with_year partner amount user *"
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
    column_names = "number_with_year entry_date " \
        "partner amount due_date user workflow_buttons *"
    insert_layout = """
    partner
    entry_date
    """
    order_by = ["-id"]


class ProjectInvoicesByJournal(InvoicesByJournal):
    column_names = "number_with_year entry_date " \
        "project partner amount due_date user workflow_buttons *"
    insert_layout = """
    project
    partner
    entry_date
    """
    detail_layout = ProjectInvoiceDetail()


VoucherTypes.add_item_lazy(InvoicesByJournal, _("Invoices"))
VoucherTypes.add_item_lazy(ProjectInvoicesByJournal, _("Project invoices"))

from lino_xl.lib.ledger.mixins import VouchersByPartnerBase

class VouchersByPartner(VouchersByPartnerBase):
    column_names = "entry_date voucher amount #state"
    # _voucher_base = AccountInvoice

    @dd.displayfield(_("Voucher"))
    def voucher(self, row, ar):
        return ar.obj2html(row)

    # if dd.plugins.ledger.project_model:
    #     @dd.virtualfield('ledger.Movement.project')
    #     def project(self, row, ar):
    #         return row.project

    @dd.virtualfield('vatless.AccountInvoice.amount')
    def amount(self, row, ar):
        return row.amount
