# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Actions for `lino_xl.lib.invoicing`.

"""


from __future__ import unicode_literals

from lino.api import dd, rt, _


class StartInvoicing(dd.Action):
    """Base for :class:`StartInvoicingForJournal`,
    :class:`StartInvoicingForPartner`.

    """
    show_in_bbar = False
    icon_name = 'basket'
    sort_index = 52
    label = _("Create invoices")
    select_rows = False
    http_method = 'POST'

    def get_options(self, ar):
        return {}

    def run_from_ui(self, ar, **kw):
        options = self.get_options(ar)
        plan = rt.modules.invoicing.Plan.start_plan(ar.get_user(), **options)
        ar.goto_instance(plan)


class StartInvoicingForJournal(StartInvoicing):
    """Start an invoicing plan for this journal.

    This is installed onto the VouchersByJournal table of the
    VoucherType for the configured
    :attr:`voucher_model<lino_xl.lib.invoicing.Plugin.voucher_model>`
    as `start_invoicing`.

    """
    show_in_bbar = True

    def get_options(self, ar):
        jnl = ar.master_instance
        assert isinstance(jnl, rt.modules.ledger.Journal)
        return dict(journal=jnl, partner=None)


class StartInvoicingForPartner(StartInvoicing):
    """Start an invoicing plan for this partner.

    This is installed onto the :class:`contacts.Partner
    <lino_xl.lib.contacts.models.Partner>` model as `start_invoicing`.

    """
    show_in_bbar = True
    select_rows = True

    def get_options(self, ar):
        partner = ar.selected_rows[0]
        assert isinstance(partner, rt.modules.contacts.Partner)
        return dict(partner=partner)


class UpdatePlan(dd.Action):
    label = _("Update plan")
    icon_name = 'lightning'
    help_text = _("Build a new list of suggestions. "
                  "This will remove all current suggestions")

    def run_from_ui(self, ar, **kw):
        plan = ar.selected_rows[0]
        plan.items.all().delete()
        plan.fill_plan(ar)
        ar.success(refresh=True)


class ExecutePlan(dd.Action):
    label = _("Execute plan")
    icon_name = 'money'

    help_text = _("Execute this invoicing plan. "
                  "Create an invoice for each selected suggestion.")

    def run_from_ui(self, ar, **kw):
        plan = ar.selected_rows[0]
        for item in plan.items.filter(selected=True, invoice__isnull=True):
            item.create_invoice(ar)
        ar.success(refresh=True)


class ExecuteItem(ExecutePlan):
    label = _("Execute item")
    show_in_workflow = True
    show_in_bbar = False
    
    help_text = _("Create an invoice for this suggestion.")

    def get_action_permission(self, ar, obj, state):
        if obj.invoice_id:
            return False
        return super(ExecuteItem, self).get_action_permission(ar, obj, state)
        
    def run_from_ui(self, ar, **kw):
        for item in ar.selected_rows:
            if item.invoice_id:
                raise Warning("Invoice was already generated")
            item.create_invoice(ar)
        ar.success(refresh=True)


class ToggleSelection(dd.Action):
    """Invert selection status for all suggestions."""
    label = _("Toggle selections")
    help_text = _("Invert selection status for all suggestions.")

    def run_from_ui(self, ar, **kw):
        plan = ar.selected_rows[0]
        for item in plan.items.all():
            item.selected = not item.selected
            item.save()
        ar.success(refresh=True)

