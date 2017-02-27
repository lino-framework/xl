# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.


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
        return rt.modules.ledger.PaymentTerm(**kwargs)
    
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
    ExcerptType = rt.modules.excerpts.ExcerptType
    ContentType = rt.modules.contenttypes.ContentType

    # yield ExcerptType(
    #     body_template="payment_reminder.body.html",
    #     content_type=ContentType.objects.get_for_model(
    #         dd.resolve_model('contacts.Partner')),
    #     **dd.str2kw('name', _("Payment reminder")))

    yield ExcerptType(
        template="payment_reminder.weasy.html",
        build_method='weasy2pdf',
        content_type=ContentType.objects.get_for_model(
            dd.resolve_model('contacts.Partner')),
        **dd.str2kw('name', _("Payment reminder")))

    yield payment_terms()


