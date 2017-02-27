# -*- coding: UTF-8 -*-
# Copyright 2016 by Luc Saffre.
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

"""Defines the :manage:`reregister` admin command:

.. management_command:: reregister

.. py2rst::

  from lino_xl.lib.ledger.management.commands.reregister \
      import Command
  print(Command.help)


"""

from __future__ import unicode_literals, print_function

from optparse import make_option
from clint.textui import progress
# from clint.textui import puts, progress

from django.core.management.base import BaseCommand  # CommandError

from lino.api import dd, rt

from lino.core.requests import BaseRequest
from lino_xl.lib.ledger.utils import check_clearings


def puts(msg):
    dd.logger.info(msg)


def reregister_vouchers(username=None, args=[], simulate=False):
    """Called by :manage:`reregister`. See there."""
    Journal = rt.models.ledger.Journal
    VoucherStates = rt.models.ledger.VoucherStates
    if len(args):
        journals = [Journal.get_by_ref(a) for a in args]
    else:
        journals = Journal.objects.order_by('seqno')
    count = 0
    clear_afterwards = True
    for jnl in journals:
        msg = "Re-register all vouchers in journal {0}".format(jnl)
        puts(msg)
        cl = jnl.get_doc_model()
        qs = cl.objects.filter(journal=jnl, state=VoucherStates.registered)
        qs = qs.order_by('entry_date')
        for obj in progress.bar(qs):
            ses = BaseRequest(user=obj.user)
            obj.register_voucher(ses, not clear_afterwards)
            count += 1

    msg = "{0} vouchers have been re-registered."
    puts(msg.format(count))

    if clear_afterwards:
        msg = "Check clearings for all partners"
        puts(msg)
        qs = rt.models.contacts.Partner.objects.all()
        for obj in progress.bar(qs):
            check_clearings(obj)


class Command(BaseCommand):
    args = "[app1.Model1] [app2.Model2] ..."
    help = """

    Re-register all ledger vouchers.

    If no arguments are given, run it on all vouchers.
    Otherwise every positional argument is expected to be a model name in
    the form `app_label.ModelName`, and only these models are being
    re-registered.

    """

    def add_arguments(self, parser):
        parser.add_argument('-s', '--simulate', action='store_true', dest='simulate',
                            default=False,
                            help="Don't actually do it. Just simulate."),

    def handle(self, *args, **options):
        reregister_vouchers(args=args, simulate=options['simulate'])
