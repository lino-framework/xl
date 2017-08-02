# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""
Model mixins for this plugin.

"""

from __future__ import unicode_literals
from __future__ import print_function

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError

from lino.utils import SumCollector
from lino.utils.dates import AMONTH, ADAY
from lino.api import dd, rt, _

from lino_xl.lib.ledger.utils import myround
from lino_xl.lib.ledger.mixins import ProjectRelated, VoucherItem
from lino_xl.lib.ledger.mixins import PeriodRange
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.sepa.mixins import Payable
from lino.mixins.periods import DateRange

from .utils import ZERO, ONE
from .choicelists import VatClasses, VatRegimes

DECLARED_IN = False

class PartnerDetailMixin(dd.DetailLayout):
    """Defines a panel :attr:`ledger`, to be added as a tab panel to your
    layout's `main` element.

    .. attribute:: ledger

        Shows the tables `VouchersByPartner` and `MovementsByPartner`.

    """
    if dd.is_installed('ledger'):
        ledger = dd.Panel("""
        payment_term
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
    """Model mixin which defines the fields `total_incl`, `total_base`
    and `total_vat`.  Used for both the document header
    (:class:`VatDocument`) and for each item (:class:`VatItemBase`).

    .. attribute:: total_incl
    
        A :class:`lino.core.fields.PriceField` which stores the total
        amount VAT *included*.

    .. attribute:: total_base

        A :class:`lino.core.fields.PriceField` which stores the total
        amount VAT *excluded*.

    .. attribute:: total_vat

        A :class:`lino.core.fields.PriceField` which stores the amount
        of VAT.

    .. method:: get_trade_type

        Subclasses of VatTotal must implement this method.

    """
    class Meta:
        abstract = True

    # price = dd.PriceField(_("Total"),blank=True,null=True)
    total_incl = dd.PriceField(_("Total incl. VAT"), blank=True, null=True)
    total_base = dd.PriceField(_("Total excl. VAT"), blank=True, null=True)
    total_vat = dd.PriceField(_("VAT"), blank=True, null=True)

    _total_fields = set('total_vat total_base total_incl'.split())
    # For internal use.  This is the list of field names to disable
    # when `auto_compute_totals` is True.

    auto_compute_totals = False
    """Set this to `True` on subclasses who compute their totals
    automatically, i.e. the fields :attr:`total_base`,
    :attr:`total_vat` and :attr:`total_incl` are disabled.  This is
    set to `True` for :class:`lino_xl.lib.sales.models.SalesDocument`.

    """

    # def get_trade_type(self):
    #     raise NotImplementedError()

    def disabled_fields(self, ar):
        """Disable all three total fields if `auto_compute_totals` is set,
        otherwise disable :attr:`total_vat` if
        :attr:`VatRule.can_edit` is False.

        """
        fields = super(VatTotal, self).disabled_fields(ar)
        if self.auto_compute_totals:
            fields |= self._total_fields
        else:
            rule = self.get_vat_rule(self.get_trade_type())
            if rule is not None and not rule.can_edit:
                fields.add('total_vat')
        return fields

    def reset_totals(self, ar):
        pass

    def get_vat_rule(self, tt):
        """Return the VAT rule for this voucher or voucher item. Called when
        user edits a total field in the document header when
        `auto_compute_totals` is False.

        """
        return None

    def total_base_changed(self, ar):
        """Called when user has edited the `total_base` field.  If total_base
        has been set to blank, then Lino fills it using
        :meth:`reset_totals`. If user has entered a value, compute
        :attr:`total_vat` and :attr:`total_incl` from this value using
        the vat rate. If there is no VatRule, `total_incl` and
        `total_vat` are set to None.

        If there are rounding differences, `total_vat` will get them.

        """
        # dd.logger.info("20150128 total_base_changed %r", self.total_base)
        if self.total_base is None:
            self.reset_totals(ar)
            if self.total_base is None:
                return

        rule = self.get_vat_rule(self.get_trade_type())
        # dd.logger.info("20150128 %r", rule)
        if rule is None:
            self.total_incl = None
            self.total_vat = None
        else:
            self.total_incl = myround(self.total_base * (ONE + rule.rate))
            self.total_vat = self.total_incl - self.total_base

    def total_vat_changed(self, ar):
        """Called when user has edited the `total_vat` field.  If it has been
        set to blank, then Lino fills it using
        :meth:`reset_totals`. If user has entered a value, compute
        :attr:`total_incl`. If there is no VatRule, `total_incl` is
        set to None.

        """
        if self.total_vat is None:
            self.reset_totals(ar)
            if self.total_vat is None:
                return

        if self.total_base is None:
            self.total_base = ZERO
        self.total_incl = self.total_vat + self.total_base

    def total_incl_changed(self, ar):
        """Called when user has edited the `total_incl` field.  If total_incl
        has been set to blank, then Lino fills it using
        :meth:`reset_totals`. If user enters a value, compute
        :attr:`total_base` and :attr:`total_vat` from this value using
        the vat rate. If there is no VatRule, `total_incl` should be
        disabled, so this method will never be called.

        If there are rounding differences, `total_vat` will get them.

        """
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


class VatDocument(ProjectRelated, VatTotal):
    auto_compute_totals = True

    refresh_after_item_edit = False

    class Meta:
        abstract = True

    vat_regime = VatRegimes.field()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(VatDocument, cls).get_registrable_fields(site):
            yield f
        yield 'vat_regime'

    if False:
        # this didn't work as expected because __init__() is called
        # also when an existing instance is being retrieved from database
        def __init__(self, *args, **kw):
            super(VatDocument, self).__init__(*args, **kw)
            self.item_vat = settings.SITE.get_item_vat(self)

    def compute_totals(self):
        if self.pk is None:
            return
        base = Decimal()
        vat = Decimal()
        tt = self.get_trade_type()
        for i in self.items.all():
            vr = i.get_vat_rule(tt)
            if i.total_base is not None:
                base += i.total_base
            if i.total_vat is not None:
                if vr is not None and not vr.vat_returnable:
                    vat += i.total_vat
        self.total_base = base
        self.total_vat = vat
        self.total_incl = vat + base

    def get_payable_sums_dict(self):
        # implements sepa.mixins.Payable
        sums = SumCollector()
        tt = self.get_trade_type()
        # vat_account = tt.get_vat_account()
        # if vat_account is None:
        #     raise Exception("No VAT account for %s." % tt)
        for i in self.items.order_by('seqno'):
            vr = i.get_vat_rule(tt)
            b = i.get_base_account(tt)
            ana_account = i.get_ana_account()
            if i.total_base:
                if b is None:
                    msg = "No base account for {0} (tt {1}, total_base {2})"
                    raise Warning(msg.format(i, tt, i.total_base))
                sums.collect(
                    ((b, ana_account), self.project, i.vat_class, self.vat_regime),
                    i.total_base)
            if i.total_vat and vr is not None:
                if not vr.vat_account:
                    msg = _("This rule ({}) does not allow any VAT.")
                    raise Warning(msg.format(vr))
                        
                vat_amount = i.total_vat
                if vr.vat_returnable:
                    if vr.vat_returnable_account is None:
                        acc_tuple = (b, ana_account)
                    else:
                        acc_tuple = (vr.vat_returnable_account, None)
                    sums.collect(
                        (acc_tuple, self.project,
                         i.vat_class, self.vat_regime),
                        vat_amount)
                    vat_amount = - vat_amount
                sums.collect(
                    ((vr.vat_account, None), self.project,
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

    def full_clean(self, *args, **kw):
        super(VatDocument, self).full_clean(*args, **kw)
        self.compute_totals()

    def before_state_change(self, ar, old, new):
        if new.name == 'registered':
            self.compute_totals()
        elif new.name == 'draft':
            pass
        super(VatDocument, self).before_state_change(ar, old, new)


class VatItemBase(VoucherItem, VatTotal):

    class Meta:
        abstract = True

    vat_class = VatClasses.field(blank=True, default=get_default_vat_class)

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
        # tt = self.voucher.get_trade_type()
        if self.vat_class is None:
            self.vat_class = self.get_vat_class(tt)

        if False:
            country = self.voucher.partner.country or \
                dd.plugins.countries.get_my_country()
        else:
            country = dd.plugins.countries.get_my_country()
        return rt.modules.vat.VatRule.get_vat_rule(
            tt, self.voucher.vat_regime, self.vat_class, country,
            self.voucher.entry_date)

    # def save(self,*args,**kw):
        # super(VatItemBase,self).save(*args,**kw)
        # self.voucher.full_clean()
        # self.voucher.save()

    def set_amount(self, ar, amount):
        self.voucher.fill_defaults()
        # rule = self.get_vat_rule()
        # if rule is None:
        #     rate = ZERO
        # else:
        #     rate = rule.rate
        if self.voucher.vat_regime.item_vat:  # unit_price_includes_vat
            self.total_incl = myround(amount)
            self.total_incl_changed(ar)
        else:
            self.total_base = myround(amount)
            self.total_base_changed(ar)

    def reset_totals(self, ar):
        if not self.voucher.auto_compute_totals:
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
        if self.voucher.refresh_after_item_edit:
            ar.set_response(refresh_all=True)
            self.voucher.compute_totals()
            self.voucher.full_clean()
            self.voucher.save()
        return kw


class QtyVatItemBase(VatItemBase):
    """Model mixin for items of a :class:`VatTotal`, adds `unit_price` and
`qty`.

    Abstract Base class for :class:`lino_xl.lib.sales.InvoiceItem` and
    :class:`lino_xl.lib.sales.OrderItem`, i.e. the lines of invoices
    *with* unit prices and quantities.

    """

    class Meta:
        abstract = True

    unit_price = dd.PriceField(_("Unit price"), blank=True, null=True)
    qty = dd.QuantityField(_("Quantity"), blank=True, null=True)

    def unit_price_changed(self, ar):
        self.reset_totals(ar)

    def qty_changed(self, ar):
        self.reset_totals(ar)

    def reset_totals(self, ar):
        super(QtyVatItemBase, self).reset_totals(ar)
        # if not self.voucher.auto_compute_totals:
        #     if self.qty:
        #         if self.voucher.item_vat:
        #             self.unit_price = self.total_incl / self.qty
        #         else:
        #             self.unit_price = self.total_base / self.qty

        if self.unit_price is not None and self.qty is not None:
            self.set_amount(ar, myround(self.unit_price * self.qty))

class VatDeclaration(Payable, Voucher, PeriodRange):

    """
    A VAT declaration is when a company declares to the state
    how much sales and purchases they've done during a given period.
    It is a summary of ledger movements.
    It is at the same time a ledger voucher.
    """

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
                    self.entry_date - AMONTH)
                
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
        """Implements
        :meth:`lino_xl.lib.sepa.mixins.Payable.get_payable_sums_dict`.

        As a side effect this updates values in the computed fields of
        this declaration.

        """
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
