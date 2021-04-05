# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime
from dateutil.relativedelta import relativedelta as delta

from decimal import Decimal

from django.conf import settings
from lino.utils import Cycler
from lino.utils.dates import AMONTH
from lino.api import dd, rt, _

from lino.modlib.uploads.mixins import demo_upload

from lino_xl.lib.vat.mixins import myround
from lino_xl.lib.ledger import UPLOADTYPE_SOURCE_DOCUMENT

# from lino.core.requests import BaseRequest
REQUEST = settings.SITE.login()  # BaseRequest()
MORE_THAN_A_MONTH = datetime.timedelta(days=40)

from lino_xl.lib.vat.choicelists import VatAreas, VatRules, VatClasses
from lino_xl.lib.ledger.choicelists import TradeTypes

def objects():

    if dd.plugins.vat.declaration_plugin is None:
        return

    # if not dd.plugins.ledger.purchase_stories:
    #     return

    Journal = rt.models.ledger.Journal
    PaymentTerm = rt.models.ledger.PaymentTerm
    Company = rt.models.contacts.Company

    USERS = Cycler(settings.SITE.user_model.objects.all())

    def func():
        # qs = Company.objects.filter(sepa_accounts__iban__isnull=False)
        # qs = Company.objects.exclude(vat_regime='').filter(
        qs = Company.objects.filter(country__isnull=False)
        for p in qs.order_by('id'):
            # if Journal.objects.filter(partner=p).exists():
            #     continue
            # if not p.vat_regime:
            #     continue
            va = VatAreas.get_for_country(p.country)
            if va is None:
                continue
            rule = VatRules.get_vat_rule(
                va, TradeTypes.purchases, p.vat_regime, default=False)
            if rule:
                yield p
    PROVIDERS = Cycler(func())

    if len(PROVIDERS) == 0:
        msg = "No providers (using declaration_plugin {}).".format(dd.plugins.vat.declaration_plugin)
        dd.logger.warning(msg)
        # raise Exception(msg)
        return

    JOURNAL_P = Journal.objects.get(ref="PRC")
    if dd.is_installed('ana'):
        ANA_ACCS = Cycler(rt.models.ana.Account.get_usable_items())
    ACCOUNTS = Cycler(JOURNAL_P.get_allowed_accounts())
    AMOUNTS = Cycler([Decimal(x) for x in
                      "20 29.90 39.90 99.95 199.95 599.95 1599.99".split()])
    AMOUNT_DELTAS = Cycler([Decimal(x)
                           for x in "0 0.60 1.10 1.30 2.50".split()])
    DATE_DELTAS = Cycler((1, 2, 3, 4, 5, 6, 7))
    INFLATION_RATE = Decimal("0.02")

    """"purchase stories" : each story represents a provider who sends
    monthly invoices.

    """
    PURCHASE_STORIES = []
    for i in range(7):
        # provider, (account,amount)
        story = (PROVIDERS.pop(), [])
        story[1].append((ACCOUNTS.pop(), AMOUNTS.pop()))
        if i % 3:
            story[1].append((ACCOUNTS.pop(), AMOUNTS.pop()))
        PURCHASE_STORIES.append(story)

    START_YEAR = dd.plugins.ledger.start_year
    date = datetime.date(START_YEAR, 1, 1)
    end_date = settings.SITE.demo_date(-10)  # + delta(years=-2)
    # end_date = datetime.date(START_YEAR+1, 5, 1)
    # print(20151216, START_YEAR, settings.SITE.demo_date(), end_date - date)

    PAYMENT_TERMS = Cycler(PaymentTerm.objects.all())
    if len(PAYMENT_TERMS) == 0:
        raise Exception("No PAYMENT_TERMS.")
    VAT_CLASSES = Cycler(VatClasses.get_list_items()[:-1])
    # 20210103 We don't use the vatless class because that would break existing doctests.

    if dd.is_installed('ana'):
        invoice_model = rt.models.ana.AnaAccountInvoice
    else:
        invoice_model = rt.models.vat.VatAccountInvoice

    while date < end_date:
        for story in PURCHASE_STORIES:
            vd = date + delta(days=DATE_DELTAS.pop())
            invoice = invoice_model(
                journal=JOURNAL_P, partner=story[0], user=USERS.pop(),
                voucher_date=vd,
                payment_term=story[0].payment_term or PAYMENT_TERMS.pop(),
                items_edited=True,
                entry_date=vd + delta(days=1))
            yield invoice
            for account, amount in story[1]:
                kwargs = dict()
                if dd.is_installed('ana'):
                    if account.needs_ana:
                        kwargs.update(ana_account=ANA_ACCS.pop())
                    model = rt.models.ana.InvoiceItem
                else:
                    model = rt.models.vat.InvoiceItem
                amount += amount + \
                    (amount * INFLATION_RATE * (date.year - START_YEAR))
                item = model(voucher=invoice,
                             account=account,
                             vat_class=VAT_CLASSES.pop(),
                             total_incl=myround(amount) +
                             AMOUNT_DELTAS.pop(), **kwargs)
                try:
                    item.total_incl_changed(REQUEST)
                except Exception as e:
                    raise
                    msg = "20171006 {} in ({} {!r})".format(
                        e, invoice.partner, invoice.vat_regime)
                    # raise Exception(msg)
                    dd.logger.warning(msg)
                else:
                    item.before_ui_save(REQUEST, None)
                    yield item
            invoice.register(REQUEST)
            invoice.save()

        date += AMONTH

    UploadType = rt.models.uploads.UploadType
    source_document = UploadType.objects.get(id=UPLOADTYPE_SOURCE_DOCUMENT)
    start_uploads = settings.SITE.demo_date(-20)
    # start_uploads = settings.SITE.demo_date().replace(month=1, day=1)
    for invoice in invoice_model.objects.filter(entry_date__gte=start_uploads):
        kw = dict(owner=invoice, upload_date=invoice.entry_date)
        yield demo_upload("{}.pdf".format(invoice), type=source_document,
            user=invoice.user, **kw)
