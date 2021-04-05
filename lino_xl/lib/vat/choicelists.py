# -*- coding: UTF-8 -*-
# Copyright 2012-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.utils import is_string
from decimal import Decimal
from lino.api import dd, _, gettext
from etgen.html import E, forcetext
from django.db import models
from lino_xl.lib.ledger.roles import LedgerStaff
from lino_xl.lib.ledger.choicelists import DC, TradeTypes, CommonAccounts

from lino_xl.lib.ledger.utils import ZERO


class VatClasses(dd.ChoiceList):
    verbose_name = _("VAT class")
    verbose_name_plural = _("VAT classes")
    required_roles = dd.login_required(LedgerStaff)
    show_values = False

add = VatClasses.add_item
add('010', _("Goods at normal VAT rate"), 'goods')    # everything else
add('020', _("Goods at reduced VAT rate"), 'reduced')  # food, books,...
add('030', _("Goods exempt from VAT"), 'exempt')    # post stamps, ...
add('100', _("Services"), 'services')
add('200', _("Investments"), 'investments')
add('210', _("Real estate"), 'real_estate')
add('220', _("Vehicles"), 'vehicles')
add('300', _("Operations without VAT"), 'vatless')  # internal clearings, flight tickets, ...



class VatAreas(dd.ChoiceList):
    verbose_name = _("VAT area")
    verbose_name_plural = _("VAT areas")
    required_roles = dd.login_required(LedgerStaff)

    @classmethod
    def get_for_country(cls, country=None):
        if country is None:
            isocode = dd.plugins.countries.country_code
        else:
            isocode = country.isocode
        if isocode == dd.plugins.countries.country_code:
            return cls.national
        if isocode in dd.plugins.vat.eu_country_codes:
            return cls.eu
        return cls.international

add = VatAreas.add_item
add('10', _("National"), 'national')
add('20', _("EU"), 'eu')
add('30', _("International"), 'international')

class VatColumn(dd.Choice):
    common_account = None

    def __init__(self, value, text, common_account=None):
        super(VatColumn, self).__init__(value, text)
        self.common_account = common_account


class VatColumns(dd.ChoiceList):
    # to be populated by bevat, bevats, ...
    verbose_name = _("VAT column")
    verbose_name_plural = _("VAT columns")
    required_roles = dd.login_required(LedgerStaff)
    show_values = True
    item_class = VatColumn
    column_names = "value text common_account account"

    @dd.virtualfield(CommonAccounts.field())
    def common_account(cls, col, ar):
        return col.common_account

    @dd.virtualfield(dd.ForeignKey('ledger.Account'))
    def account(cls, col, ar):
        if col.common_account is not None:
            return col.common_account.get_object()


class VatRegime(dd.Choice):
    vat_area = None
    needs_vat_id = False
    # item_vat = True  # 20200521 no longer used

    def __init__(self, value, text, name, vat_area=None, item_vat=True, needs_vat_id=False):
        super(VatRegime, self).__init__(value, text, name)
        self.vat_area = vat_area
        self.needs_vat_id = needs_vat_id
        # self.item_vat = item_vat

    def is_allowed_for(self, vat_area):
        if self.vat_area is None:
            return True
        return self.vat_area == vat_area


class VatRegimes(dd.ChoiceList):
    verbose_name = _("VAT regime")
    verbose_name_plural = _("VAT regimes")
    column_names = "value name text vat_area needs_vat_id #item_vat"
    item_class = VatRegime
    required_roles = dd.login_required(LedgerStaff)

    @dd.virtualfield(VatAreas.field())
    def vat_area(cls, regime, ar):
        return regime.vat_area

    # @dd.virtualfield(dd.BooleanField(_("item VAT")))
    # def item_vat(cls, regime, ar):
    #     return regime.item_vat

    @dd.virtualfield(dd.BooleanField(_("Needs VAT id")))
    def needs_vat_id(cls, regime, ar):
        return regime.needs_vat_id


add = VatRegimes.add_item
add('10', _("Normal"), 'normal')
# re-populated in bevat and bevats.
# See also lino_xl.lib.vat.Plugin.default_vat_regime

#
class DeclarationField(dd.Choice):
    editable = False
    vat_regimes = None
    exclude_vat_regimes = None
    vat_classes = None
    exclude_vat_classes = None
    vat_columns = None
    exclude_vat_columns = None
    is_payable = False
    # value dc vat_columns text fieldnames both_dc vat_regimes vat_classes
    def __init__(self, value, dc,
                 vat_columns=None,
                 # is_base,
                 text=None,
                 fieldnames='',
                 both_dc=True,
                 vat_regimes=None, vat_classes=None,
                 **kwargs):
        name = "F" + value
        # text = string_concat("[{}] ".format(value), text)
        self.help_text = text
        super(DeclarationField, self).__init__(
            value, "[{}]".format(value), name, **kwargs)

        # self.is_base = is_base
        self.fieldnames = fieldnames
        self.vat_regimes = vat_regimes
        self.vat_classes = vat_classes
        self.vat_columns = vat_columns
        self.dc = dc
        self.both_dc = both_dc

    def attach(self, choicelist):
        self.minus_observed_fields = set()
        self.observed_fields = []
        for n in self.fieldnames.split():
            if n.startswith('-'):
                n = n[1:]
                self.minus_observed_fields.add(n)
            f = choicelist.get_by_value(n)
            if f is None:
                raise Exception(
                    "Invalid observed field {} for {}".format(n, self))
            self.observed_fields.append(f)

        if is_string(self.vat_regimes):
            vat_regimes = self.vat_regimes
            self.vat_regimes = set()
            self.exclude_vat_regimes = set()
            for n in vat_regimes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_regimes
                    n = n[1:]
                else:
                    s = self.vat_regimes
                v = VatRegimes.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT regime {} for field {}".format(
                            v, self.value))
                s.add(v)
            if len(self.vat_regimes) == 0:
                self.vat_regimes = None
            if len(self.exclude_vat_regimes) == 0:
                self.exclude_vat_regimes = None

        if is_string(self.vat_classes):
            vat_classes = self.vat_classes
            self.vat_classes = set()
            self.exclude_vat_classes = set()
            for n in vat_classes.split():
                if n.startswith('!'):
                    s = self.exclude_vat_classes
                    n = n[1:]
                else:
                    s = self.vat_classes
                v = VatClasses.get_by_name(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT class {} for field {}".format(
                            v, self.value))
                s.add(v)
            if len(self.vat_classes) == 0:
                self.vat_classes = None
            if len(self.exclude_vat_classes) == 0:
                self.exclude_vat_classes = None

        # using VAT columns as selector is probably obsolete
        if is_string(self.vat_columns):
            vat_columns = self.vat_columns
            self.vat_columns = set()
            self.exclude_vat_columns = set()
            for n in vat_columns.split():
                if n.startswith('!'):
                    s = self.exclude_vat_columns
                    n = n[1:]
                else:
                    s = self.vat_columns
                v = VatColumns.get_by_value(n)
                if v is None:
                    raise Exception(
                        "Invalid VAT column {} for field {}".format(
                            n, self.value))
                s.add(v)
            if len(self.vat_columns) == 0:
                self.vat_columns = None
            if len(self.exclude_vat_columns) == 0:
                self.exclude_vat_columns = None

        super(DeclarationField, self).attach(choicelist)


    def get_model_field(self):
        return dd.PriceField(
            self.text, default=Decimal, editable=self.editable,
            help_text=self.help_text)

    # def __str__(self):
    #     # return force_str(self.text, errors="replace")
    #     # return self.text
    #     return "[{}] {}".format(self.value, self.text)

    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        pass

    def collect_from_sums(self, dcl, sums, payable_sums):
        pass

class SumDeclarationField(DeclarationField):

    def __init__(self, *args, **kwargs):
        super(SumDeclarationField, self).__init__(*args, **kwargs)
        if self.is_payable:
            raise Exception("SumDeclarationField may not be payable")

    def collect_from_sums(self, dcl, field_values, payable_sums):
        tot = Decimal()
        for f in self.observed_fields:
            v = field_values[f.name]
            if f.value in self.minus_observed_fields:
                v = -v
            tot += v
            # if f.dc == self.dc:
            #     tot += v
            # else:
            #     tot -= v
        field_values[self.name] = tot

class WritableDeclarationField(DeclarationField):
    editable = True
    def collect_from_sums(self, dcl, field_values, payable_sums):
        if self.is_payable:
            amount = field_values[self.name]
            if amount:
                if self.dc == dcl.journal.dc:
                    amount = - amount
                k = ((dcl.journal.account, None), None, None, None)
                payable_sums.collect(k, amount)

class MvtDeclarationField(DeclarationField):

    def collect_from_movement(self, dcl, mvt, field_values, payable_sums):
        # if not mvt.account.declaration_field in self.observed_fields:
        #     return 0
        if self.vat_classes is not None:
            if not mvt.vat_class in self.vat_classes:
                return
        if self.exclude_vat_classes is not None:
            if mvt.vat_class in self.exclude_vat_classes:
                return
        if self.vat_columns is not None:
            if not mvt.account.vat_column in self.vat_columns:
                return
        if self.exclude_vat_columns is not None:
            if mvt.account.vat_column in self.exclude_vat_columns:
                return
        if self.vat_regimes is not None:
            if not mvt.vat_regime in self.vat_regimes:
                return
        if self.exclude_vat_regimes is not None:
            if mvt.vat_regime in self.exclude_vat_regimes:
                return
        amount = mvt.amount
        if not amount:
            return
        if self.dc == DC.debit:
            amount = -amount
        if amount < 0 and not self.both_dc:
            return
        field_values[self.name] += amount
        if self.is_payable:
            if self.dc == dcl.journal.dc:
                amount = - amount
            # k = ((mvt.account, None), mvt.project, mvt.vat_class, mvt.vat_regime)
            k = ((mvt.account, None), None, None, None)
            payable_sums.collect(k, amount)
            # k = (dcl.journal.account, None, None, None)
            # payable_sums.collect(k, amount)


# class AccountDeclarationField(MvtDeclarationField):
#     pass
    # def __init__(self, value, dc, vat_columns, *args, **kwargs):
    #     # kwargs.update(fieldnames=value)
    #     kwargs.update(vat_columns=vat_columns)
    #     super(AccountDeclarationField, self).__init__(
    #         value, dc, *args, **kwargs)



class DeclarationFieldsBase(dd.ChoiceList):
    verbose_name_plural = _("Declaration fields")
    item_class = DeclarationField
    column_names = "value name text description *"

    # @classmethod
    # def add_account_field(cls, *args, **kwargs):
    #     cls.add_item_instance(
    #         AccountDeclarationField(*args, **kwargs))

    @classmethod
    def add_mvt_field(cls, *args, **kwargs):
        cls.add_item_instance(
            MvtDeclarationField(*args, **kwargs))

    @classmethod
    def add_sum_field(cls, *args, **kwargs):
        cls.add_item_instance(
            SumDeclarationField(*args, **kwargs))


    @classmethod
    def add_writable_field(cls, *args, **kwargs):
        cls.add_item_instance(
            WritableDeclarationField(*args, **kwargs))


    @dd.displayfield(_("Description"))
    def description(cls, fld, ar):
        if ar is None:
            return ''
        elems = [fld.help_text, E.br()]
        def x(label, lst, xlst):
            if lst is None:
                spec = ''
            else:
                lst = sorted([i.name or i.value for i in lst])
                spec = ' '.join(lst)
            if xlst is not None:
                xlst = sorted(["!"+(i.name or i.value) for i in xlst])
                spec += ' ' + ' '.join(xlst)
            spec = spec.strip()
            if spec:
                elems.extend([label, " ", spec, E.br()])

        x(_("columns"), fld.vat_columns, fld.exclude_vat_columns)
        x(_("regimes"), fld.vat_regimes, fld.exclude_vat_regimes)
        x(_("classes"), fld.vat_classes, fld.exclude_vat_classes)


        elems += [
            fld.__class__.__name__, ' ',
            str(fld.dc),
            "" if fld.both_dc else " only",
            E.br()]

        if len(fld.observed_fields):
            names = []
            for f in fld.observed_fields:
                n = f.value
                if f.value in fld.minus_observed_fields:
                    n = "- " + n
                elif len(names) > 0:
                    n = "+ " + n
                names.append(n)
            elems += ['= ', ' '.join(names), E.br()]

        return E.div(*forcetext(elems))


class VatRule(dd.Choice):
    start_date = None
    end_date= None
    vat_area = None
    trade_type = None
    vat_class = None
    vat_regime = None
    rate = ZERO
    vat_account = None
    # vat_returnable = None
    vat_returnable_account = None

    def __init__(self,
                 vat_class=None, rate=None,
                 vat_area=None, trade_type=None,
                 vat_regime=None, vat_account=None,
                 vat_returnable_account=None):
        kw = dict(vat_area=vat_area)
        if rate is not None:
            kw.update(rate=Decimal(rate))
        # if vat_returnable is None:
        #     vat_returnable = vat_returnable_account is not None
        # kw.update(vat_returnable=vat_returnable)
        if trade_type:
            kw.update(trade_type=TradeTypes.get_by_name(trade_type))
        if vat_regime:
            kw.update(vat_regime=VatRegimes.get_by_name(vat_regime))
        if vat_class:
            kw.update(vat_class=VatClasses.get_by_name(vat_class))
        if vat_account:
            kw.update(vat_account=vat_account)
        if vat_returnable_account:
            kw.update(vat_returnable_account=vat_returnable_account)
        # text = "{trade_type} {vat_area} {vat_class} {rate}".format(**kw)
        super(VatRule, self).__init__(None, None, **kw)

    def __str__(rule):
        lst = []
        only = []
        lst.append(gettext("VAT rule {}: ".format(rule.value)))
        if rule.trade_type is not None:
            only.append(str(rule.trade_type))
        if rule.vat_regime is not None:
            only.append(str(rule.vat_regime))
        if rule.vat_area is not None:
            only.append(str(rule.vat_area))
        if rule.vat_class is not None:
            only.append(str(rule.vat_class))
        if len(only):
            lst.append(gettext("if ({}) then".format(', '.join(only))))
        lst.append(gettext("apply {} %".format(rule.rate)))
        lst.append(gettext("and book to {}").format(rule.vat_account))
        if rule.vat_returnable_account is not None:
            lst.append(gettext("(return to {})").format(rule.vat_returnable_account))
        return '\n'.join(lst)

    #     kw = dict(
    #         trade_type=self.trade_type,
    #         vat_regime=self.vat_regime,
    #         vat_class=self.vat_class,
    #         rate=self.rate,
    #         vat_area=self.vat_area, seqno=self.seqno)
    #     return "{trade_type} {vat_area} {vat_class} {rate}".format(**kw)


class VatRules(dd.ChoiceList):
    verbose_name = _("VAT rule")
    verbose_name_plural = _("VAT rules")
    item_class = VatRule
    column_names = "value description"

    @classmethod
    def get_vat_rule(
            cls, vat_area,
            trade_type=None, vat_regime=None, vat_class=None,
            date=None, default=models.NOT_PROVIDED):
        for i in cls.get_list_items():
            if i.vat_area is not None and vat_area != i.vat_area:
                continue
            if i.trade_type is not None and trade_type != i.trade_type:
                continue
            if i.vat_class is not None and vat_class != i.vat_class:
                continue
            if i.vat_regime is not None and vat_regime != i.vat_regime:
                continue
            if date is not None:
                if i.start_date and i.start_date > date:
                    continue
                if i.end_date and i.end_date < date:
                    continue
            return i
        if default is models.NOT_PROVIDED:
            msg = _("No VAT rule for ({!r},{!r},{!r},{!r},{!r})").format(
                    trade_type, vat_class, vat_area, vat_regime,
                    dd.fds(date))
            if False:
                dd.logger.info(msg)
            else:
                raise Warning(msg)
        return default

    @dd.displayfield(_("Description"))
    def description(cls, rule, ar):
        return str(rule)


# we add a single rule with no rate and no conditions, iow any combination is
# allowed and no vat is applied. The declaration modules will clear this list
# and fill it with their rules.

VatRules.add_item()
