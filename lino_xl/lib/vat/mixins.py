# -*- coding: UTF-8 -*-
# Copyright 2012-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from lino.utils import SumCollector
# from lino.utils.dates import AMONTH, ADAY
from lino.api import dd, rt, _
# from lino.mixins.registrable import Registrable

from lino_xl.lib.ledger.choicelists import CommonAccounts
from lino_xl.lib.ledger.mixins import ProjectRelated, VoucherItem
from lino_xl.lib.ledger.mixins import Payable
from lino_xl.lib.ledger.models import RegistrableVoucher, VoucherStates
from lino_xl.lib.ledger.utils import ZERO, ONE, myround

from .choicelists import VatClasses, VatRegimes, VatAreas, VatRules

ledger = dd.resolve_app("ledger")

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


# def get_default_vat_class():
#     return dd.plugins.vat.default_vat_class


class VatTotal(dd.Model):
    # abstract base class for both voucher and item
    class Meta:
        abstract = True

    total_incl = dd.PriceField(_("Total to pay"), blank=True, null=True)
    total_base = dd.PriceField(_("Total excl. VAT"), blank=True, null=True)
    total_vat = dd.PriceField(_("VAT"), blank=True, null=True)

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
            if rule.vat_returnable_account is not None:
                self.total_incl = self.total_base
                self.total_vat = None
            else:
                self.total_vat = myround(self.total_base * rule.rate)
                self.total_incl = self.total_base + self.total_vat

    def total_vat_changed(self, ar):
        if self.total_vat is None:
            self.reset_totals(ar)
            if self.total_vat is None:
                return

        if self.total_base is None:
            self.total_base = ZERO
        rule = self.get_vat_rule(self.get_trade_type())
        if rule is not None and rule.vat_returnable_account is not None:
            self.total_incl = self.total_base
            self.total_vat = None
        else:
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
            if rule.vat_returnable_account is not None:
                self.total_base = self.total_incl
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


class VatDocument(RegistrableVoucher, ProjectRelated, VatTotal):

    # refresh_after_item_edit = False

    class Meta:
        abstract = True

    state = VoucherStates.field(default='draft')
    vat_regime = VatRegimes.field()
    items_edited = models.BooleanField(default=False)

    edit_totals = True

    compute_sums = ComputeSums()

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(VatDocument, cls).get_registrable_fields(site):
            yield f
        yield 'vat_regime'

    def compute_totals(self):
        if self.pk is None or not self.state.is_editable:
            return
        # print("20190911 compute_totals")
        base = Decimal()
        vat = Decimal()
        # tt = self.get_trade_type()
        for i in self.items.all():
            if i.total_base is not None:
                base += i.total_base
            if i.total_vat is not None:
                vat += i.total_vat
        self.total_base = myround(base)
        self.total_vat = myround(vat)
        self.total_incl = myround(base + vat)

    def get_payable_sums_dict(self):
        # implements sepa.mixins.Payable
        sums = SumCollector()
        tt = self.get_trade_type()
        # vat_account = tt.get_vat_account()
        # if vat_account is None:
        #     raise Exception("No VAT account for %s." % tt)
        for i in self.items.order_by('seqno'):
            rule = i.get_vat_rule(tt)
            base_account = i.get_base_account(tt)
            ana_account = i.get_ana_account()
            if i.total_base:
                if base_account is None:
                    msg = "No base account for {0} (tt {1}, total_base {2})"
                    raise Warning(msg.format(i, tt, i.total_base))
                sums.collect(
                    ((base_account, ana_account), self.project, i.vat_class, self.vat_regime),
                    i.total_base)

            if rule is not None:
                if rule.vat_returnable_account is None:
                    vat_amount = i.total_vat
                else:
                    vat_amount = myround(i.total_base * rule.rate)
                if not vat_amount:
                    continue

                if rule.vat_returnable_account is not None:
                    acc_tuple = (rule.vat_returnable_account.get_object(), None)
                    sums.collect(
                        (acc_tuple, self.project, i.vat_class, self.vat_regime),
                        - vat_amount)
                if rule.vat_account is None:
                    acc_tuple = (base_account, ana_account)
                else:
                    acc_tuple = (rule.vat_account.get_object(), None)
                sums.collect(
                    (acc_tuple, self.project, i.vat_class, self.vat_regime),
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
        return rt.models.vat.get_vat_regime_choices(partner.country)

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
        if self.vat_regime is not None:
            if self.vat_regime.needs_vat_id and not self.partner.vat_id:
                raise ValidationError(
                    _("Cannot use VAT regime {} for partner without VAT id").format(
                    self.vat_regime))

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

# dd.update_field(VatDocument, 'total_incl', verbose_name=_("Total to pay"))


class VatVoucher(VatDocument, Payable):
    # todo: merge VatDocument and VatVoucher?
    class Meta:
        abstract = True


class VatItemBase(VoucherItem, VatTotal):

    class Meta:
        abstract = True

    vat_class = VatClasses.field(blank=True)  # , default=get_default_vat_class)
    # item_total = dd.field_alias('total_incl' if dd.plugins.vat.item_vat else 'total_base')

    def delete(self, **kw):
        super(VatItemBase, self).delete(**kw)
        v = self.voucher
        if v.edit_totals and v.items_edited:
            if not v.items.exists():
                v.items_edited = False
                v.save()

    def get_trade_type(self):
        return self.voucher.get_trade_type()

    def get_default_vat_class(self, tt):
        acc = self.get_base_account(tt)
        if acc and acc.vat_class:
            return acc.vat_class
        return dd.plugins.vat.get_vat_class(tt, self)

    def vat_class_changed(self, ar):
        # dd.logger.info("20121204 vat_class_changed")
        # if self.voucher.vat_regime.item_vat:
        if dd.plugins.vat.item_vat:
            self.total_incl_changed(ar)
        else:
            self.total_base_changed(ar)

    def get_base_account(self, tt):
        raise NotImplementedError

    def get_vat_rule(self, tt):
        if self.vat_class is None:
            self.vat_class = self.get_default_vat_class(tt)
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
        # if self.voucher.vat_regime.item_vat:  # unit_price_includes_vat
        if dd.plugins.vat.item_vat:
            return self.total_incl
        return self.total_base

    def set_amount(self, ar, amount):
        self.voucher.fill_defaults()
        # if self.voucher.vat_regime.item_vat:  # unit_price_includes_vat
        if dd.plugins.vat.item_vat:  # unit_price_includes_vat
            self.total_incl = myround(amount)
            self.total_incl_changed(ar)
        else:
            self.total_base = myround(amount)
            self.total_base_changed(ar)

    def reset_totals(self, ar):
        # if self.voucher.items_edited:
        if self.voucher.edit_totals and self.voucher.total_incl:
            rule = self.get_vat_rule(self.get_trade_type())
            qs = self.voucher.items.exclude(id=self.id)
            if rule.vat_returnable_account is not None:
                total = qs.aggregate(models.Sum('total_base'))['total_base__sum'] or Decimal()
                self.total_base = self.voucher.total_incl - total
                self.total_base_changed(ar)
            else:
                total = qs.aggregate(models.Sum('total_incl'))['total_incl__sum'] or Decimal()
                self.total_incl = self.voucher.total_incl - total
                self.total_incl_changed(ar)
        super(VatItemBase, self).reset_totals(ar)

    def full_clean(self):
        if self.vat_class is None:
            self.vat_class = self.get_default_vat_class(self.get_trade_type())
        super(VatItemBase, self).full_clean()

    def before_ui_save(self, ar, cw):
        if self.total_incl is None:
            self.reset_totals(ar)
        super(VatItemBase, self).before_ui_save(ar, cw)

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


class VatDeclaration(ledger.Declaration):

    class Meta:
        abstract = True

    def get_payable_sums_dict(self):
        # side effect : calling this will also update the fields and save the
        # declaration.
        fields = self.fields_list.get_list_items()
        payable_sums = SumCollector()
        sums = dict()  # field sums
        for fld in fields:
            if fld.editable:
                sums[fld.name] = getattr(self, fld.name)
            else:
                sums[fld.name] = Decimal('0.00')  # ZERO

        flt = self.get_period_filter(
            'voucher__',
            # voucher__journal__preliminary=False,
            voucher__journal__must_declare=True)


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

        for fld in fields:
            if not fld.editable:
                setattr(self, fld.name, sums[fld.name])

        # side effect!:
        self.full_clean()
        self.save()

        return payable_sums

    def print_declared_values(self):
        # used in doctests
        for fld in self.fields_list.get_list_items():
            v = getattr(self, fld.name)
            if v:
                print("[{}] {} : {}".format(fld.value, fld.help_text, v))
