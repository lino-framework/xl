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
from lino_xl.lib.ledger.models import Voucher
from lino_xl.lib.sepa.mixins import Payable
from lino.mixins.periods import DatePeriod

from .utils import ZERO, ONE
from .choicelists import VatClasses, VatRegimes


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
    """Abstract base class for invoices, offers and other vouchers.

    .. attribute:: partner

       Mandatory field to be defined in another class.

    .. attribute:: refresh_after_item_edit

        The total fields of an invoice are currently not automatically
        updated each time an item is modified.  Users must click the
        Save or the Register button to see the invoices totals.

        One idea is to have
        :meth:`lino_xl.lib.vat.models.VatItemBase.after_ui_save`
        insert a `refresh_all=True` (into the response to the PUT or
        POST coming from Lino.GridPanel.on_afteredit).
        
        This has the disadvantage that the cell cursor moves to the
        upper left corner after each cell edit.  We can see how this
        feels by setting :attr:`refresh_after_item_edit` to `True`.

    .. attribute:: vat_regime

        The VAT regime to be used in this document.  A pointer to
        :class:`VatRegimes`.

    """

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
                if not vr.vat_returnable_account:
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
            if i.total_base:
                b = i.get_base_account(tt)
                if b is None:
                    msg = "No base account for {0} (tt {1}, total_base {2})"
                    raise Exception(msg.format(i, tt, i.total_base))
                sums.collect(
                    (b, self.project, i.vat_class, self.vat_regime),
                    i.total_base)
            if i.total_vat:
                if not vr.vat_account:
                    raise Exception("No VAT account for %s." % vr)
                sums.collect(
                    (vr.vat_account, self.project,
                     i.vat_class, self.vat_regime),
                    i.total_vat)
                if vr.vat_returnable_account:
                    sums.collect(
                        (vr.vat_returnable_account, self.project,
                         i.vat_class, self.vat_regime),
                        - i.total_vat)
        return sums

    def fill_defaults(self):
        super(VatDocument, self).fill_defaults()
        if not self.vat_regime:
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
    """Model mixin for items of a :class:`VatTotal`.

    Abstract Base class for
    :class:`lino_xl.lib.ledger.models.InvoiceItem`, i.e. the lines of
    invoices *without* unit prices and quantities.

    Subclasses must define a field called "voucher" which must be a
    ForeignKey with related_name="items" to the "owning document",
    which in turn must be a subclass of :class:`VatDocument`).

    .. attribute:: vat_class

        The VAT class to be applied for this item. A pointer to
        :class:`VatClasses`.

    """

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
        """Return the `VatRule` which applies for this item.

        `tt` is the trade type (which is the same for each item of a
        voucher, that's why we expect the caller to provide it).

        This basically calls the class method
        :meth:`VatRule.get_vat_rule
        <lino_xl.lib.vat.models.VatRule.get_vat_rule>` with
        appropriate arguments.

        When selling certain products ("automated digital services")
        in the EU, you have to pay VAT in the buyer's country at that
        country's VAT rate.  See e.g.  `How can I comply with VAT
        obligations?
        <https://ec.europa.eu/growth/tools-databases/dem/watify/selling-online/how-can-i-comply-vat-obligations>`_.
        TODO: Add a new attribute `VatClass.buyers_country` or a
        checkbox `Product.buyers_country` or some other way to specify
        this.

        """

        # tt = self.voucher.get_trade_type()
        if self.vat_class is None:
            self.vat_class = self.get_vat_class(tt)

        if False:
            country = self.voucher.partner.country or \
                dd.plugins.countries.get_my_country()
        else:
            country = dd.plugins.countries.get_my_country()
        rule = rt.modules.vat.VatRule.get_vat_rule(
            tt, self.voucher.vat_regime, self.vat_class, country,
            self.voucher.voucher_date)
        return rule

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
        """
        """
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


class VatDeclaration(Voucher, DatePeriod, Payable):

    """
    A VAT declaration is when a company declares to the state
    how much sales and purchases they've done during a given period.
    It is a summary of ledger movements.
    It is at the same time a ledger voucher.
    """

    class Meta:
        abstract = True
        
    def full_clean(self, *args, **kw):
        if self.voucher_date:
            # declare the previous month by default 
            if not self.start_date:
                self.start_date = (self.voucher_date-AMONTH).replace(day=1)
            if not self.end_date:
                self.end_date = self.start_date + AMONTH - ADAY
        if self.voucher_date <= self.end_date:
           raise ValidationError(
               "Voucher date must be after the covered period")
        self.compute_fields()
        super(VatDeclaration, self).full_clean(*args, **kw)

    def get_payable_sums_dict(self):
        """Implements
        :meth:`lino_xl.lib.sepa.mixins.Payable.get_payable_sums_dict`.

        """
        mvt_dict = {}
        for fld in self.fields_list.get_list_items():
            fld.collect_wanted_movements(self, mvt_dict)
        return mvt_dict

    def get_wanted_movements(self):
        # dd.logger.info("20151211 FinancialVoucher.get_wanted_movements()")
        
        # TODO: not yet implemented.
        return []
        amount = ZERO
        movements_and_items = []
        
        for i in self.items.all():
            if i.dc == self.journal.dc:
                amount += i.amount
            else:
                amount -= i.amount
            # kw = dict(seqno=i.seqno, partner=i.partner)
            kw = dict(partner=i.get_partner())
            kw.update(match=i.match or i.get_default_match())
            b = self.create_movement(
                i, i.account or self.item_account,
                i.project, i.dc, i.amount, **kw)
            movements_and_items.append((b, i))

        return amount, movements_and_items
    

    def unused_register_voucher(self, *args, **kwargs):
        super(VatDeclaration, self).register_voucher(*args, **kwargs)
        self.compute_fields()
        if False:
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

    def unused_deregister_voucher(self, *args, **kwargs):
        super(VatDeclaration, self).deregister_voucher(*args, **kwargs)
        if False:
            for doc in rt.models.ledger.Voucher.objects.filter(
                    declared_in=self):
                doc.declared_in = None
                doc.save()
            
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

        
    def compute_fields(self):
        sums = dict()
        fields = self.fields_list.get_list_items()
        for fld in fields:
            if fld.editable:
                sums[fld.name] = getattr(self, fld.name)
            else:
                sums[fld.name] = ZERO

        qs = rt.models.ledger.Movement.objects.filter(
            # voucher__journal=jnl,
            # voucher__year=self.accounting_period.year,
            voucher__journal__must_declare=True,
            voucher__entry_date__gte=self.start_date,
            voucher__entry_date__lte=self.end_date)
            # voucher__declared_in__isnull=True)

        for mvt in qs:
            for fld in fields:
                amount = fld.collect_movement(self, mvt)
                if amount:
                    sums[fld.name] += amount
            
        for fld in fields:
            fld.collect_from_sums(self, sums)

        #~ print 20121209, item_models
        #~ for m in item_models:
        #~ for m in rt.models_by_base(VatDocument):
            #~ for item in m.objects.filter(voucher__declaration=self):
                #~ logger.info("20121208 b document %s",doc)
                #~ self.collect_item(sums,item)

        for fld in fields:
            setattr(self, fld.name, sums[fld.name])

