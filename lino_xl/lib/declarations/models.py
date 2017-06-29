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

from lino.api import dd, rt
from django.utils.translation import ugettext_lazy as _
from lino.mixins.periods import DatePeriod

# partner_model = settings.SITE.partners_app_label + '.Partner'

vat = dd.resolve_app('vat')
ledger = dd.resolve_app('ledger')

ZERO = Decimal()

from .choicelists import DeclarationFields


class Declaration(ledger.Voucher, DatePeriod):

    """
    A VAT declaration is when a company declares to the state
    how much sales and purchases they've done during a given period.
    It is a summary of ledger movements.
    It is at the same time a ledger voucher.
    """

    #~ fields_list = DeclarationFields

    class Meta:
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

    def get_wanted_movements(self):
        # dd.logger.info("20151211 FinancialVoucher.get_wanted_movements()")
        amount, movements_and_items = self.get_finan_movements()
        if amount:
            raise Warning(_("Missing amount {} in movements").format(
                amount))
        for m, i in movements_and_items:
            yield m

    def register_voucher(self, *args, **kwargs):
        super(Declaration, self).register_voucher(*args, **kwargs)
        self.compute_fields()
        count = 0
        for doc in rt.models.ledger.Voucher.objects.filter(
            # journal=jnl,
            # year=self.accounting_period.year,
            # entry_date__month=month,
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

    def get_wanted_movements(self):
        return []  # TODO
        
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

# importing the country module will fill DeclarationFields
import_module(dd.plugins.declarations.country_module)

for fld in DeclarationFields.objects():
    dd.inject_field(Declaration, fld.name, fld.get_model_field())

dd.inject_field('ledger.Voucher',
                'declared_in',
                models.ForeignKey(Declaration,
                                  blank=True, null=True))

dd.inject_field('accounts.Account',
                'declaration_field',
                DeclarationFields.field(blank=True, null=True))



