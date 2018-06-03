# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre


"""

.. xfile:: payment_reminder.body.html

  Defines the body text of a payment reminder.

.. xfile:: base.weasy.html
.. xfile:: payment_reminder.weasy.html

  Defines the body text of a payment reminder.

"""

from __future__ import unicode_literals

from lino.api import dd, rt, _


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

    yield ExcerptType(
        template="payment_reminder.weasy.html",
        build_method='weasy2pdf',
        content_type=ContentType.objects.get_for_model(Partner),
        **dd.str2kw('name', _("Payment reminder")))

    yield payment_terms()


