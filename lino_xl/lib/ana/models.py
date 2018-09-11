# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
# from django.core.exceptions import ValidationError

from lino.api import dd, rt

from lino.mixins import Referrable, Sequenced, StructuredReferrable
from lino.utils.mldbc.mixins import BabelDesignated
from lino_xl.lib.ledger.choicelists import VoucherTypes
from lino_xl.lib.ledger.ui import AccountBalances
from lino_xl.lib.ledger.mixins import ItemsByVoucher
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
# from lino_xl.lib.ledger.fields import DebitOrCreditField
# from lino_xl.lib.ledger.utils import DEBIT


# class Group(BabelDesignated, Referrable):
#     ref_max_length = 10
#     class Meta:
#         verbose_name = _("Analytical account group")
#         verbose_name_plural = _("Analytical account groups")


# class Groups(dd.Table):
#     model = 'ana.Group'
#     required_roles = dd.login_required(LedgerStaff)
#     stay_in_grid = True
#     order_by = ['ref']
#     column_names = 'ref designation *'

#     insert_layout = """
#     designation
#     ref
#     """

#     detail_layout = """
#     ref designation id
#     AccountsByGroup
#     """


# @dd.python_2_unicode_compatible
class Account(StructuredReferrable, BabelDesignated, Sequenced):
    ref_max_length = settings.SITE.plugins.ana.ref_length

    class Meta:
        verbose_name = _("Analytical account")
        verbose_name_plural = _("Analytical accounts")
        ordering = ['ref']

    # group = dd.ForeignKey(
    #     'ana.Group', verbose_name=_("Group"), blank=True, null=True)
    # normal_dc = DebitOrCreditField(
    #     _("Normal booking direction"), default=DEBIT)

    # def full_clean(self, *args, **kw):
    #     if self.group_id is not None:
    #         if not self.ref:
    #             qs = rt.models.ana.Account.objects.all()
    #             self.ref = str(qs.count() + 1)
    #         if not self.designation:
    #             self.designation = self.group.designation

    #     # if self.default_dc is None:
    #     #     self.default_dc = self.type.dc
    #     super(Account, self).full_clean(*args, **kw)

    # def __str__(self):
    #     return "({ref}) {title}".format(
    #         ref=self.ref, title=dd.babelattr(self, 'designation'))


class Accounts(dd.Table):
    model = 'ana.Account'
    required_roles = dd.login_required(LedgerStaff)
    stay_in_grid = True
    order_by = ['ref']
    column_names = "ref designation *"
    insert_layout = """
    ref 
    designation
    """
    detail_layout = """
    ref designation id
    ana.MovementsByAccount
    """


class MovementsByAccount(dd.Table):
    model = 'ledger.Movement'
    master_key = 'ana_account'


from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.mixins import Matching, AccountVoucherItem
from lino_xl.lib.sepa.mixins import Payable
from lino_xl.lib.vat.mixins import VatDocument, VatItemBase
from lino_xl.lib.ledger.ui import PartnerVouchers, ByJournal, PrintableByJournal


# class MakeCopy(dd.Action):
#     button_text = u"\u2042"  # ASTERISM (⁂)
    
#     label = _("Make copy")
#     show_in_workflow = True
#     show_in_bbar = False
#     copy_item_fields = set('account ana_account total_incl seqno'.split())
    
#     parameters = dict(
#         partner=dd.ForeignKey('contacts.Partner'),
#         account=dd.ForeignKey('ledger.Account', blank=True),
#         ana_account=dd.ForeignKey('ana.Account', blank=True),
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
#     subject total_incl
#     account ana_account 
#     """

#     def action_param_defaults(self, ar, obj, **kw):
#         kw = super(MakeCopy, self).action_param_defaults(ar, obj, **kw)
#         kw.update(your_ref=obj.your_ref)
#         kw.update(subject=obj.narration)
#         kw.update(entry_date=obj.entry_date)
#         kw.update(partner=obj.partner)
#         # qs = obj.items.all()
#         # if qs.count():
#         #     kw.update(product=qs[0].product)
#         # kw.update(total_incl=obj.total_incl)
#         return kw

#     # def partner_changed(self, ar, obj, **kw):
#     #     pass
    
#     def run_from_ui(self, ar, **kw):
#       # raise Warning("20180802")

#         VoucherStates = rt.models.ledger.VoucherStates
#         obj = ar.selected_rows[0]
#         pv = ar.action_param_values
#         kw = dict(
#             journal=obj.journal,
#             user=ar.get_user(),
#             partner=pv.partner, entry_date=pv.entry_date,
#             narration=pv.subject,
#             your_ref=pv.your_ref)

#         new = obj.__class__(**kw)
#         new.fill_defaults()
#         new.full_clean()
#         new.save()
#         if pv.total_incl:
#             if not pv.account:
#                 tt = obj.journal.trade_type
#                 pv.account = tt.get_partner_invoice_account(pv.partner)
#             if pv.account:
#                 if not pv.ana_account:
#                     pv.ana_account = pv.account.ana_account
#             else:
#                 qs = obj.items.all()
#                 if qs.count():
#                     pv.account = qs[0].account
#                     if not pv.ana_account:
#                         pv.ana_account = qs[0].ana_account
#             if not pv.account.needs_ana:
#                 pv.ana_account = None
#             item = new.add_voucher_item(
#                 total_incl=pv.total_incl, account=pv.account,
#                 seqno=1,
#                 ana_account=pv.ana_account)
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
        


class AnaAccountInvoice(VatDocument, Payable, Voucher, Matching):
    class Meta:
        verbose_name = _("Analytic invoice")
        verbose_name_plural = _("Analytic invoices")

    # make_copy = MakeCopy()
    # probably no longer needed because now we have
    # VatDocument.items_edited

        
class InvoiceItem(AccountVoucherItem, VatItemBase):
    class Meta:
        app_label = 'ana'
        verbose_name = _("Analytic invoice item")
        verbose_name_plural = _("Analytic invoice items")

    voucher = dd.ForeignKey('ana.AnaAccountInvoice', related_name='items')
    ana_account = dd.ForeignKey('ana.Account', blank=True, null=True)
    title = models.CharField(_("Description"), max_length=200, blank=True)

    def full_clean(self, *args, **kwargs):
        super(InvoiceItem, self).full_clean(*args, **kwargs)
        if self.account_id and self.account.needs_ana:
            if not self.ana_account_id:
                if self.account.ana_account_id:
                    self.ana_account = self.account.ana_account

    def get_ana_account(self):
        return self.ana_account

    def account_changed(self, ar=None):
        if self.account_id:
            if self.account.needs_ana:
                # if the general account an analytic one but has no
                # default value (needs_ana is checked but ana_account
                # empty), leave the current one.
                if self.account.ana_account:
                    self.ana_account = self.account.ana_account
            else:
                self.ana_account = None
            
    


class InvoiceDetail(dd.DetailLayout):
    main = "general ledger"

    general = dd.Panel("""
    topleft:60 totals:20
    ItemsByInvoice 
    """, label=_("General"))
    
    totals = """
    total_base
    total_vat
    total_incl
    """

    topleft = """number entry_date #voucher_date partner
    payment_term due_date your_ref vat_regime
    workflow_buttons user
    """

    ledger = dd.Panel("""
    journal accounting_period id narration
    ledger.MovementsByVoucher
    """, label=_("Ledger"))


class Invoices(PartnerVouchers):
    """The table of all
    :class:`VatAccountInvoice<lino_xl.lib.vat.models.VatAccountInvoice>`
    objects.

    """
    required_roles = dd.login_required(LedgerUser)
    model = 'ana.AnaAccountInvoice'
    order_by = ["-id"]
    column_names = "entry_date number_with_year partner total_incl user id *"
    detail_layout = 'ana.InvoiceDetail'
    insert_layout = """
    journal partner
    entry_date total_incl
    """
    # start_at_bottom = True


class InvoicesByPartner(Invoices):
    master_key = 'partner'
    
class InvoicesByJournal(ByJournal, Invoices):
    """Shows all invoices of a given journal (whose
    :attr:`voucher_type<lino_xl.lib.ledger.models.Journal.voucher_type>`
    must be :class:`lino_xl.lib.vat.models.VatAccountInvoice`)

    """
    # order_by = ["-accounting_period__year", "-number"]
    params_layout = "partner state year"
    column_names = "number_with_year entry_date due_date " \
        "partner " \
        "total_incl " \
        "total_base total_vat user workflow_buttons *"
                  #~ "ledger_remark:10 " \
    insert_layout = """
    partner
    entry_date total_incl
    """

from django.db.models import OuterRef

class AnalyticAccountBalances(AccountBalances, Accounts):

    label = _("Analytic Account Balances")
    model = 'ana.Account'
    order_by = ['ref']

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     return rt.models.ana.Account.objects.order_by(
    #         'group__ref', 'ref')

    @classmethod
    def rowmvtfilter(self, row):
        # return dict(ana_account=row)
        return dict(ana_account=OuterRef('pk'))

    # @dd.displayfield(_("Ref"))
    # def ref(self, row, ar):
    #     return ar.obj2html(row.group)


                  

VoucherTypes.add_item_lazy(InvoicesByJournal)

class PrintableInvoicesByJournal(PrintableByJournal, Invoices):
    label = _("Purchase journal (analytic)")


    
class ItemsByInvoice(ItemsByVoucher):
    model = 'ana.InvoiceItem'
    column_names = "account title ana_account vat_class total_base total_vat total_incl *"
    display_mode = 'grid'



dd.inject_field(
    'ledger.Movement', 'ana_account',
    dd.ForeignKey('ana.Account', blank=True, null=True))

dd.inject_field(
    'ledger.Account', 'ana_account',
    dd.ForeignKey('ana.Account', blank=True, null=True))

dd.inject_field(
    'ledger.Account', 'needs_ana',
    models.BooleanField(_("Needs analytical account"), default=False))

# if dd.is_installed('vat'):
    
#     dd.inject_field(
#         'vat.InvoiceItem', 'ana_account',
#         dd.ForeignKey('ana.Account', blank=True, null=True))

