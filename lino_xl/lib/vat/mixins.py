# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from decimal import Decimal

from django.conf import settings
from django.db import models
# from django.core.exceptions import ValidationError

from lino.utils import SumCollector
# from lino.utils.dates import AMONTH, ADAY
from lino.api import dd, rt, _

from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.ledger.utils import myround
from lino_xl.lib.ledger.choicelists import CommonAccounts
from lino_xl.lib.ledger.mixins import ProjectRelated, VoucherItem
from lino_xl.lib.ledger.mixins import PeriodRange
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.ledger.utils import ZERO, ONE
from lino_xl.lib.sepa.mixins import Payable

from .choicelists import VatClasses, VatRegimes, VatAreas, VatRules

DECLARED_IN = False

class PartnerDetailMixin(dd.DetailLayout):
    """
    Defines a panel :attr:`ledger`, to be added as a tab panel to your
    layout's `main` element.

    .. attribute:: ledger

        Shows the tables `VouchersByPartner` and `MovementsByPartner`.
    """
    if dd.is_installed('ledger'):
        ledger = dd.Panel("""
        payment_term purchase_account
        vat.VouchersByPartner
        ledger.MovementsByPartner
        """, label=dd.plugins.ledger.verbose_name)
    else:
        ledger = dd.DummyPanel()


def get_default_vat_regime():
    return dd.plugins.vat.default_vat_regime


def get_default_vat_class():
    return dd.plugins.vat.default_vat_class


class VatTotal(dd.Model):
    # abstract base class for both voucher and item
    class Meta:
        abstract = True

    # price = dd.PriceField(_("Total"),blank=True,null=True)
    total_incl = dd.PriceField(_("Total incl. VAT"), blank=True, null=True)
    total_base = dd.PriceField(_("Total excl. VAT"), blank=True, null=True)
    total_vat = dd.PriceField(_("VAT"), blank=True, null=True)

    _total_fields = set('total_vat total_base total_incl'.split())
    # For internal use.  This is the list of field names to disable
    # when `edit_totals` is False.

    edit_totals = True

    # def get_trade_type(self):
    #     raise NotImplementedError()

    def disabled_fields(self, ar):
        fields = super(VatTotal, self).disabled_fields(ar)
        if self.edit_totals:
            rule = self.get_vat_rule(self.get_trade_type())
            if rule is None:
                fields.add('total_vat')
                fields.add('total_base')
            elif not rule.can_edit:
                fields.add('total_vat')
        else:
            fields |= self._total_fields
        return fields

    def reset_totals(self, ar):
        pass

    def get_vat_rule(self, tt):
        return None

    def total_base_changed(self, ar):
        # dd.logger.info("20150128 total_base_changed %r", self.total_base)
        if self.total_base is None:
            self.reset_totals(ar)
            if self.total_base is None:
                return

        rule = self.get_vat_rule(self.get_trade_type())
        # dd.logger.info("20180813 %r", rule)
        if rule is None:
            self.total_incl = None
            self.total_vat = None
        else:
            self.total_incl = myround(self.total_base * (ONE + rule.rate))
            self.total_vat = self.total_incl - self.total_base

    def total_vat_changed(self, ar):
        if self.total_vat is None:
            self.reset_totals(ar)
            if self.total_vat is None:
                return

        if self.total_base is None:
            self.total_base = ZERO
        self.total_incl = self.total_vat + self.total_base

    def total_incl_changed(self, ar):
        if self.total_incl is None:
            self.reset_totals(ar)
            if self.total_incl is None:
                return
        # assert not isinstance(self.total_incl,basestring)
        rule = self.get_vat_rule(self.get_trade_type())
        if rule is None:
            self.total_base = None
            self.total_vat = None
        else:
            self.total_base = myround(self.total_incl / (ONE + rule.rate))
            self.total_vat = myround(self.total_incl - self.total_base)
            

class ComputeSums(dd.Action):
    help_text = _("Compute sums")
    button_text = "Σ"
    custom_handler = True
    readonly = False
    
    def get_action_permission(self, ar, obj, st):
        # if ar.data_iterator is None:
        #     return False
        if not super(ComputeSums, self).get_action_permission(ar, obj, st):
            return False
        return True

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        obj.compute_totals()
        obj.full_clean()
        obj.save()
        ar.success(refresh=True)
        
        
class VatDocument(ProjectRelated, VatTotal):

    # refresh_after_item_edit = False

    class Meta:
        abstract = True

    vat_regime = VatRegimes.field()
    items_edited = models.BooleanField(default=False)
    compute_sums = ComputeSums()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(VatDocument, cls).get_registrable_fields(site):
            yield f
        yield 'vat_regime'

    def compute_totals(self):
        if self.pk is None or not self.state.is_editable:
            return
        base = Decimal()
        vat = Decimal()
        for i in self.items.all():
            if i.total_base is not None:
                base += i.total_base
            if i.total_vat is not None:
                vat += i.total_vat
        self.total_base = myround(base)
        self.total_vat = myround(vat)
        self.total_incl = myround(vat + base)

    def get_payable_sums_dict(self):
        # implements sepa.mixins.Payable
        sums = SumCollector()
        tt = self.get_trade_type()
        # vat_account = tt.get_vat_account()
        # if vat_account is None:
        #     raise Exception("No VAT account for %s." % tt)
        for i in self.items.order_by('seqno'):
            rule = i.get_vat_rule(tt)
            b = i.get_base_account(tt)
            ana_account = i.get_ana_account()
            if i.total_base:
                if b is None:
                    msg = "No base account for {0} (tt {1}, total_base {2})"
                    raise Warning(msg.format(i, tt, i.total_base))
                sums.collect(
                    ((b, ana_account), self.project, i.vat_class, self.vat_regime),
                    i.total_base)
            if i.total_vat and rule is not None:
                if not rule.vat_account:
                    msg = _("This rule ({}) does not allow any VAT.")
                    raise Warning(msg.format(rule))
                        
                vat_amount = i.total_vat
                if rule.vat_returnable:
                    if rule.vat_returnable_account is None:
                        acc_tuple = (b, ana_account)
                    else:
                        acc_tuple = (
                            rule.vat_returnable_account.get_object(), None)
                    sums.collect(
                        (acc_tuple, self.project,
                         i.vat_class, self.vat_regime),
                        vat_amount)
                    vat_amount = - vat_amount
                sums.collect(
                    ((rule.vat_account.get_object(), None), self.project,
                     i.vat_class, self.vat_regime),
                    vat_amount)
        return sums

    def fill_defaults(self):
        super(VatDocument, self).fill_defaults()
        if not self.vat_regime:
            if self.partner_id:
                self.vat_regime = self.partner.vat_regime
            if not self.vat_regime:
                self.vat_regime = get_default_vat_regime()

    def update_item(self):
        if self.pk is None or not self.state.is_editable:
            return
        if self.items_edited or not self.edit_totals:
            return
        tt = self.journal.trade_type
        account = tt.get_partner_invoice_account(self.partner)
        if account is None:
            account = CommonAccounts.waiting.get_object()
            if account is None:
                raise Warning(
                    _("{} is not configured").format(
                        CommonAccounts.waiting))
        kw = dict()
        if dd.is_installed('ana') and account.needs_ana:
            kw['ana_account'] = account.ana_account
        kw['account'] = account
        kw['total_incl'] = self.total_incl
        qs = self.items.all()
        if qs.count():
            item = qs[0]
            for k, v in kw.items():
                setattr(item, k, v)
        else:
            item = self.add_voucher_item(seqno=1, **kw)
        item.total_incl_changed(None)
        item.full_clean()
        item.save()

    @dd.chooser()
    def vat_regime_choices(self, partner):
        return rt.models.vat.get_vat_regime_choices(
            partner, partner.country, partner.vat_id)

    def partner_changed(self, ar=None):
        self.vat_regime = None
        self.fill_defaults()
        # self.update_item()  # called by after_ui_save()
        
    def after_ui_save(self, ar, cw):
        self.update_item()
        return super(VatDocument, self).after_ui_save(ar, cw)
        
        
    def full_clean(self, *args, **kw):
        super(VatDocument, self).full_clean(*args, **kw)
        if not self.edit_totals:
            self.compute_totals()

    def before_state_change(self, ar, old, new):
        if new.name == 'registered':
            self.compute_totals()
            
            self.items_edited = True
            # Above line is because an automatically filled invoice
            # item should not change anymore once the invoice has been
            # registered.  For example if the partner's
            # purchase_account changed and you unregister an old
            # invoice, Lino must not automatically replace the account
            # of that invoice.
            
        elif new.name == 'draft':
            if not self.edit_totals:
                self.total_base = None
                self.total_vat = None
                self.total_incl = None
        super(VatDocument, self).before_state_change(ar, old, new)


class VatItemBase(VoucherItem, VatTotal):

    class Meta:
        abstract = True

    vat_class = VatClasses.field(blank=True, default=get_default_vat_class)

    def delete(self, **kw):
        super(VatItemBase, self).delete(**kw)
        v = self.voucher
        if v.edit_totals and v.items_edited:
            if not v.items.exists():
                v.items_edited = False
                v.save()

    def get_trade_type(self):
        return self.voucher.get_trade_type()

    def get_vat_class(self, tt):
        return dd.plugins.vat.get_vat_class(tt, self)

    def vat_class_changed(self, ar):
        # dd.logger.info("20121204 vat_class_changed")
        if self.voucher.vat_regime.item_vat:
            self.total_incl_changed(ar)
        else:
            self.total_base_changed(ar)

    def get_base_account(self, tt):
        raise NotImplementedError

    def get_vat_rule(self, tt):
        if self.vat_class is None:
            self.vat_class = self.get_vat_class(tt)
            # we store it because there might come more calls, but we
            # don't save it because here's not the place to decide
            # this.
            
        # country = self.voucher.partner.country or \
        #           dd.plugins.countries.get_my_country()
        vat_area = VatAreas.get_for_country(
            self.voucher.partner.country)
        return VatRules.get_vat_rule(
            vat_area,
            trade_type=tt,
            vat_regime=self.voucher.vat_regime,
            vat_class=self.vat_class, 
            date=self.voucher.entry_date)

    # def save(self,*args,**kw):
        # super(VatItemBase,self).save(*args,**kw)
        # self.voucher.full_clean()
        # self.voucher.save()

    def get_amount(self):
        if self.voucher.vat_regime.item_vat:  # unit_price_includes_vat
            return self.total_incl
        return self.total_base
            
    def set_amount(self, ar, amount):
        self.voucher.fill_defaults()
        if self.voucher.vat_regime.item_vat:  # unit_price_includes_vat
            self.total_incl = myround(amount)
            self.total_incl_changed(ar)
        else:
            self.total_base = myround(amount)
            self.total_base_changed(ar)

    def reset_totals(self, ar):
        # if self.voucher.items_edited:
        if self.voucher.edit_totals and self.voucher.total_incl:
            total = Decimal()
            for item in self.voucher.items.exclude(id=self.id):
                total += item.total_incl
            # if total != self.voucher.total_incl:
            self.total_incl = self.voucher.total_incl - total
            self.total_incl_changed(ar)

        super(VatItemBase, self).reset_totals(ar)

    def before_ui_save(self, ar):
        if self.total_incl is None:
            self.reset_totals(ar)
        super(VatItemBase, self).before_ui_save(ar)

    def after_ui_save(self, ar, cw):
        """
        After editing a grid cell automatically show new invoice totals.
        """
        kw = super(VatItemBase, self).after_ui_save(ar, cw)
        if self.voucher.edit_totals and not self.voucher.items_edited:
            self.voucher.items_edited = True
            self.voucher.save()
        # if self.voucher.refresh_after_item_edit:
        #     ar.set_response(refresh_all=True)
        #     self.voucher.compute_totals()
        #     self.voucher.full_clean()
        #     self.voucher.save()
        return kw


class QtyVatItemBase(VatItemBase):

    class Meta:
        abstract = True

    unit_price = dd.PriceField(_("Unit price"), blank=True, null=True)
    qty = dd.QuantityField(_("Quantity"), blank=True, null=True)

    def unit_price_changed(self, ar=None):
        self.reset_totals(ar)

    def qty_changed(self, ar=None):
        self.reset_totals(ar)

    def reset_totals(self, ar=None):
        super(QtyVatItemBase, self).reset_totals(ar)
        # if self.voucher.edit_totals:
        #     if self.qty:
        #         if self.voucher.item_vat:
        #             self.unit_price = self.total_incl / self.qty
        #         else:
        #             self.unit_price = self.total_base / self.qty

        if self.unit_price is not None:
            if self.qty is None:
                self.set_amount(ar, myround(self.unit_price))
            else:
                self.set_amount(ar, myround(self.unit_price * self.qty))


class VatDeclaration(Payable, Voucher, Certifiable, PeriodRange):

    class Meta:
        abstract = True
        
    def get_match(self):
        return self.get_default_match()  # no manual match field

    def full_clean(self, *args, **kw):
        if self.entry_date:
            AP = rt.models.ledger.AccountingPeriod
            # declare the previous month by default 
            if not self.start_period_id:
                self.start_period = AP.get_default_for_date(
                    self.entry_date)
                # self.start_period = AP.get_default_for_date(
                #     self.entry_date - AMONTH)
                
            # if not self.start_date:
            #     self.start_date = (self.voucher_date-AMONTH).replace(day=1)
            # if not self.end_date:
            #     self.end_date = self.start_date + AMONTH - ADAY
        # if self.voucher_date <= self.end_date:
        #    raise ValidationError(
        #        "Voucher date must be after the covered period")
        # self.compute_fields()
        super(VatDeclaration, self).full_clean(*args, **kw)

    def register_voucher(self, *args, **kwargs):
        # self.compute_fields()
        if DECLARED_IN:
            count = 0
            for doc in rt.models.ledger.Voucher.objects.filter(
                # journal=jnl,
                # year=self.accounting_period.year,
                # entry_date__month=month,
                journal__must_declare=True,
                entry_date__gte=self.start_date,
                entry_date__lte=self.end_date,
                declared_in__isnull=True
            ):
                #~ logger.info("20121208 a can_declare %s",doc)
                count += 1
                doc.declared_in = self
                doc.save()
                #~ declared_docs.append(doc)
        if False: # write match to declared movements
            flt = self.get_period_filter(
                'voucher__accounting_period',
                match='',
                account__clearable=True,
                account__needs_partner=False,
                voucher__journal__must_declare=True)
            qs = rt.models.ledger.Movement.objects.filter(**flt)
            for mvt in qs:
                mvt.match = self.get_match()
                mvt.save()
        super(VatDeclaration, self).register_voucher(*args, **kwargs)
                

    def deregister_voucher(self, *args, **kwargs):
        if DECLARED_IN:
            for doc in rt.models.ledger.Voucher.objects.filter(
                    declared_in=self):
                doc.declared_in = None
                doc.save()
                
        if False:  # remove match from declared movements
            flt = self.get_period_filter(
                'voucher__accounting_period',
                match=self.get_match(),
                account__clearable=True,
                account__needs_partner=False,
                voucher__journal__must_declare=True)
            qs = rt.models.ledger.Movement.objects.filter(**flt)
            for mvt in qs:
                mvt.match = ''
                mvt.save()
            
        # deregister
        super(VatDeclaration, self).deregister_voucher(*args, **kwargs)
                
            
    # def before_state_change(self, ar, old, new):
    #     if new.name == 'register':
    #         self.compute_fields()
    #     elif new.name == 'draft':
    #     super(Declaration, self).before_state_change(ar, old, new)

    #~ def register(self,ar):
        #~ self.compute_fields()
        #~ super(Declaration,self).register(ar)
        #~
    #~ def deregister(self,ar):
        #~ for doc in ledger.Voucher.objects.filter(declared_in=self):
            #~ doc.declared_in = None
            #~ doc.save()
        #~ super(Declaration,self).deregister(ar)

        
    def get_payable_sums_dict(self):
        fields = self.fields_list.get_list_items()
        payable_sums = SumCollector()
        sums = dict()  # field sums
        for fld in fields:
            if fld.editable:
                sums[fld.name] = getattr(self, fld.name)
            else:
                sums[fld.name] = Decimal('0.00')  # ZERO

        flt = self.get_period_filter(
            'voucher__accounting_period',
            # voucher__journal=jnl,
            # voucher__year=self.accounting_period.year,
            voucher__journal__must_declare=True)
            # voucher__declared_in__isnull=True)


        qs = rt.models.ledger.Movement.objects.filter(**flt)
        qs = qs.order_by('voucher__journal', 'voucher__number')

        # print(20170713, qs)

        for mvt in qs:
            for fld in fields:
                fld.collect_from_movement(
                    self, mvt, sums, payable_sums)
                # if fld.is_payable:
                #     print("20170802 after {} {} : {}".format(
                #         fld, mvt.amount, payable_sums))
            
        for fld in fields:
            fld.collect_from_sums(self, sums, payable_sums)

        # dd.logger.info("20170713 value in 55 is %s", sums['F55'])

        #~ print 20121209, item_models
        #~ for m in item_models:
        #~ for m in rt.models_by_base(VatDocument):
            #~ for item in m.objects.filter(voucher__declaration=self):
                #~ logger.info("20121208 b document %s",doc)
                #~ self.collect_item(sums,item)

        for fld in fields:
            if not fld.editable:
                setattr(self, fld.name, sums[fld.name])

        # self.full_clean()
        # self.save()
        return payable_sums
