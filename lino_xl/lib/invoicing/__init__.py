# -*- coding: UTF-8 -*-
# Copyright 2016-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds functionality for **invoicing**, i.e. automatically generating
invoices from data in the database.

See :doc:`/specs/invoicing`.

"""

from lino.api.ad import Plugin, _
from django.utils.text import format_lazy


class Plugin(Plugin):

    verbose_name = _("Invoicing")

    # needs_plugins = ['lino_xl.lib.ledger']
    needs_plugins = ['lino_xl.lib.sales']

    voucher_model = 'sales.VatProductInvoice'
    item_model = 'sales.InvoiceItem'
    """
    The database model into which invoiceable objects should create
    invoice items.  Default value refers to :class:`sales.InvoiceItem
    <lino_xl.lib.sales.models.InvoiceItem>`.

    This model will have an injected GFK field `invoiceable`.
    """

    invoiceable_label = _("Invoiced object")

    def on_site_startup(self, site):
        from lino.core.utils import resolve_model
        self.item_model = resolve_model(self.item_model)
        # ivm = self.item_model._meta.get_field('voucher').remote_field.model
        # if self.voucher_model != ivm:
        #     raise Exception("voucher_model is {} but should be {}".format(
        #         self.voucher_model, ivm))
        self.voucher_model = resolve_model(self.voucher_model)

    def get_voucher_type(self):
        # from lino.core.utils import resolve_model
        # model = resolve_model(self.voucher_model)
        # return self.site.modules.ledger.VoucherTypes.get_for_model(model)
        return self.site.models.ledger.VoucherTypes.get_for_model(
            self.voucher_model)

    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.sales
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m.add_action('invoicing.MyPlans')
        m.add_action('invoicing.Plan', action='start_plan')

        # Area = site.models.invoicing.Area
        # # Areas = site.models.invoicing.Areas
        # for obj in Area.objects.all():
        #     # m.add_instance_action(obj, action='start_invoicing')
        #     # m.add_action(obj, action='start_invoicing')
        #     m.add_action(
        #         'invoicing.PlansByArea', 'start_invoicing',
        #         label=format_lazy(_("Create invoices {}"), obj),
        #         params=dict(master_instance=obj))

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.sales
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('invoicing.Tariffs')
        m.add_action('invoicing.Areas')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.sales
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('invoicing.AllPlans')
        m.add_action('invoicing.SalesRules')
