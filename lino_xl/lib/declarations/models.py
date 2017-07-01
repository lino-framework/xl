# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


"""Database models for `lino_xl.lib.vat`.

This module defines some central ChoiceLists and Model mixins designed
to work both with and without :mod:`lino_xl.lib.ledger` installed.

"""

from __future__ import unicode_literals

from importlib import import_module
from decimal import Decimal
from dateutil.relativedelta import relativedelta as delta
AMONTH = delta(months=1)
ADAY = delta(days=1)

from django.db import models
# from django.conf import settings
from django.core.exceptions import ValidationError

from lino.utils import SumCollector
from lino.api import dd, rt, _
from lino.mixins.periods import DatePeriod

# partner_model = settings.SITE.partners_app_label + '.Partner'
from lino_xl.lib.sepa.mixins import Payable

vat = dd.resolve_app('vat')
ledger = dd.resolve_app('ledger')

ZERO = Decimal()

from .choicelists import DeclarationFields


class Declaration(ledger.Voucher, DatePeriod, Payable):

    """
    A VAT declaration is when a company declares to the state
    how much sales and purchases they've done during a given period.
    It is a summary of ledger movements.
    It is at the same time a ledger voucher.
    """

    #~ fields_list = DeclarationFields

    class Meta:
        app_label = 'declarations'
        verbose_name = _("VAT declaration")
        verbose_name_plural = _("VAT declarations")
        
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
        super(Declaration, self).full_clean(*args, **kw)

    def get_payable_sums_dict(self):
        """To be implemented by subclasses.  Expected to return a dict which
        maps 5-tuples `(account, project, is_base, vat_class,
        vat_regime)` to the amount. is_base, vat_class and vat_regime
        are needed by :mod:`lino_xl.lib.declarations`.

        """
        mvt_dict = {}
        for fld in DeclarationFields.get_list_items():
            fld.collect_wanted_movements(self, mvt_dict)

    def get_wanted_movements(self):
        # dd.logger.info("20151211 FinancialVoucher.get_wanted_movements()")
        
        return []

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
    

    def register_voucher(self, *args, **kwargs):
        super(Declaration, self).register_voucher(*args, **kwargs)
        self.compute_fields()
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

    def deregister_voucher(self, *args, **kwargs):
        super(Declaration, self).deregister_voucher(*args, **kwargs)
        for doc in rt.models.ledger.Voucher.objects.filter(declared_in=self):
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
        for fld in DeclarationFields.objects():
            sums[fld.name] = ZERO

        qs = ledger.Movement.objects.filter(
            # voucher__journal=jnl,
            # voucher__year=self.accounting_period.year,
            voucher__journal__must_declare=True,
            voucher__entry_date__gte=self.start_date,
            voucher__entry_date__lte=self.end_date,
            voucher__declared_in__isnull=True)

        for mvt in qs:
            for fld in DeclarationFields.get_list_items():
                amount = fld.collect_movement(self, mvt)
                if amount:
                    sums[fld.name] += amount
            
        for fld in DeclarationFields.get_list_items():
            fld.collect_from_sums(self, sums)

        #~ print 20121209, item_models
        #~ for m in item_models:
        #~ for m in rt.models_by_base(VatDocument):
            #~ for item in m.objects.filter(voucher__declaration=self):
                #~ logger.info("20121208 b document %s",doc)
                #~ self.collect_item(sums,item)

        for fld in DeclarationFields.get_list_items():
            setattr(self, fld.name, sums[fld.name])

# if dd.is_installed('declarations'): # avoid autodoc failure
#     # importing the country module will fill DeclarationFields
#     import_module(dd.plugins.declarations.country_module)

dd.inject_field('ledger.Voucher',
                'declared_in',
                models.ForeignKey(Declaration,
                                  blank=True, null=True))

dd.inject_field('accounts.Account',
                'declaration_field',
                DeclarationFields.field(blank=True, null=True))


# dd.inject_field('ledger.Journal',
#                 'declared',
#                 models.BooleanField(default=True))

