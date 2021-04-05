# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime

from django.conf import settings

from lino.api import dd, rt, _
from lino_xl.lib.ledger.choicelists import CommonAccounts
from lino_xl.lib.ledger import UPLOADTYPE_SOURCE_DOCUMENT


def update(ci, **kwargs):
    obj = ci.get_object()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


def payment_terms():
    """Loads a default list of payment terms
    (:class:`lino_xl.lib.ledger.models.PaymentTerm`).

    """
    def PT(name, ref, **kwargs):
        kwargs['ref'] = ref
        kwargs = dd.str2kw('name', name, **kwargs)
        return rt.models.ledger.PaymentTerm(**kwargs)

    yield PT(_("Payment in advance"), "PIA")
    yield PT(_("Payment seven days after invoice date"), "07", days=7)
    yield PT(_("Payment ten days after invoice date"), "10", days=10)
    yield PT(_("Payment 30 days after invoice date"), "30", days=30)
    yield PT(_("Payment 60 days after invoice date"), "60", days=60)
    yield PT(_("Payment 90 days after invoice date"), "90", days=90)
    yield PT(_("Payment end of month"), "EOM", end_of_month=True)
    prt = """Prepayment <b>30%</b>
    ({{(obj.total_incl*30)/100}} {{obj.currency}})
    due on <b>{{fds(obj.due_date)}}</b>, remaining
    {{obj.total_incl - (obj.total_incl*30)/100}} {{obj.currency}}
    due 10 days before delivery.
    """
    yield PT(_("Prepayment 30%"), "P30", days=30, printed_text=prt)


def objects():
    ExcerptType = rt.models.excerpts.ExcerptType
    ContentType = rt.models.contenttypes.ContentType
    Partner = rt.models.contacts.Partner
    FiscalYear = rt.models.ledger.FiscalYear

    UploadType = rt.models.uploads.UploadType

    kw = dict()
    kw.update(max_number=1, wanted=True)
    kw.update(dd.str2kw('name', _("Source document")))
    yield UploadType(id=UPLOADTYPE_SOURCE_DOCUMENT, **kw)


    cfg = dd.plugins.ledger
    site = settings.SITE
    if site.the_demo_date is not None:
        if cfg.start_year > site.the_demo_date.year:
            raise Exception(
                "plugins.ledger.start_year is after the_demo_date")
    today = site.the_demo_date or datetime.date.today()
    for y in range(cfg.start_year, today.year + 6):
        yield FiscalYear.create_from_year(y)
        # FiscalYears.add_item(FiscalYear.year2value(y), str(y))

    yield ExcerptType(
        template="payment_reminder.weasy.html",
        build_method='weasy2pdf',
        content_type=ContentType.objects.get_for_model(Partner),
        **dd.str2kw('name', _("Payment reminder")))

    # yield ExcerptType(
    #     template="annual_report.weasy.html",
    #     build_method='weasy2pdf',
    #     content_type=ContentType.objects.get_for_model(FiscalYear),
    #     **dd.str2kw('name', _("Annual report")))

    # yield ExcerptType(
    #     template="annual_report.weasy.html",
    #     build_method='weasy2pdf',
    #     content_type=ContentType.objects.get_for_model(
    #         rt.models.ledger.Report),
    #     **dd.str2kw('name', _("Annual report")))

    yield payment_terms()

    # populate accounts from CommonAccounts, then manually set
    # sales_allowed, purchases_allowed and needs_ana

    for i in CommonAccounts.get_list_items():
        yield i.create_object()

    # delete one account object to get a MissingAccount in tests
    CommonAccounts.net_loss.get_object().delete()
    CommonAccounts.net_loss.set_object(None)

    kwargs = dict(purchases_allowed=True)
    if dd.is_installed('ana'):
        kwargs.update(needs_ana=True)
    yield update(CommonAccounts.purchase_of_goods, **kwargs)
    yield update(CommonAccounts.purchase_of_services, **kwargs)
    yield update(CommonAccounts.purchase_of_investments, **kwargs)

    kwargs = dict(sales_allowed=True)
    yield update(CommonAccounts.sales, **kwargs)

    # # add some header accounts
    # Account = rt.models.ledger.Account
    # def account(ref, designation):
    #     return Account(ref=ref, **dd.str2kw('name', designation))
    # yield account("4", _("Commercial assets & liabilities"))
    # yield account("5", _("Financial assets & liabilities"))
    # yield account("6", _("Expenses"))
    # yield account("60", _("Operation costs"))
    # yield account("61", _("Wages"))
    # yield account("7", _("Revenues"))
