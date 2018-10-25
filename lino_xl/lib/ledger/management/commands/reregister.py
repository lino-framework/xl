# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Defines the :manage:`reregister` admin command:

.. management_command:: reregister

.. py2rst::

  from lino_xl.lib.ledger.management.commands.reregister \
      import Command
  print(Command.help)


"""

from __future__ import unicode_literals, print_function

from clint.textui import progress

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from atelier.utils import confirm
from lino.api import dd, rt

from lino.core.requests import BaseRequest
from lino_xl.lib.ledger.models import check_clearings_by_partner


def puts(msg):
    dd.logger.info(msg)


def reregister_vouchers(args):
    """Called by :manage:`reregister`. See there."""
    Journal = rt.models.ledger.Journal
    VoucherStates = rt.models.ledger.VoucherStates
    if len(args):
        journals = [Journal.get_by_ref(a) for a in args]
    else:
        journals = Journal.objects.order_by('seqno')
        rt.models.ledger.Movement.objects.all().delete()
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
            check_clearings_by_partner(obj)


class Command(BaseCommand):
    args = "[jnlref1] [jnlref2] ..."
    help = """

    Re-register all ledger vouchers.

    If no arguments are given, run it on all vouchers.  Otherwise
    every positional argument is expected to be the ref of a journal,
    and are being re-registered.

    When called with no arguments, all movements are deleted from the
    database.  This can help if the database contains movments with
    invalid voucher pointer.

    """

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_false',
                            dest='interactive', default=True,
                            help='Do not prompt for input of any kind.'),
        # parser.add_argument('-s', '--simulate', action='store_true', dest='simulate',
        #                     default=False,
        #                     help="Don't actually do it. Just simulate."),

    def handle(self, *args, **options):
        if options.get('interactive'):
            using = options.get('database', DEFAULT_DB_ALIAS)
            dbname = settings.DATABASES[using]['NAME']
            if not confirm(
                    "This is going to rebuild all ledger movements "
                    "in %s. Are you sure (y/n) ?" % dbname):
                raise CommandError("User abort.")
            
        reregister_vouchers(args)
