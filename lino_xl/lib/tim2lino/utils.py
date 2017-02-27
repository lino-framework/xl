# -*- coding: UTF-8 -*-
# Copyright 2009-2015 Luc Saffre
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

"""Import legacy data from TIM (basic version).
"""

import traceback
import os
from clint.textui import puts, progress
from django.conf import settings
from atelier.utils import AttrDict
from lino.api import dd, rt
from lino.utils import dbfreader


class TimLoader(object):

    LEN_IDGEN = 6

    archived_tables = set()
    archive_name = None
    codepage = 'cp850'
    # codepage = 'cp437'
    # etat_registered = "C"¹
    etat_registered = "¹"

    def __init__(self, dbpath, languages=None):
        self.dbpath = dbpath
        self.VENDICT = dict()
        self.FINDICT = dict()
        self.GROUPS = dict()
        self.languages = dd.resolve_languages(
            languages or dd.plugins.tim2lino.languages)
        self.must_register = []
        self.must_match = {}
        self.duplicate_zip_codes = dict()

    def finalize(self):
        if len(self.duplicate_zip_codes):
            for country, codes in self.duplicate_zip_codes.items():
                dd.logger.warning(
                    "%d duplicate zip codes in %s : %s",
                    len(codes), country, ', '.join(codes))
            
        ses = rt.login(self.ROOT.username)

        Journal = rt.models.ledger.Journal
        dd.logger.info("Register %d vouchers", len(self.must_register))
        failures = 0
        for doc in progress.bar(self.must_register):
            # puts("Registering {0}".format(doc))
            try:
                doc.register(ses)
            except Exception as e:
                dd.logger.warning("Failed to register %s : %s ", doc, e)
                failures += 1
                if failures > 100:
                    dd.logger.warning("Abandoned after 100 failures.")
                    break

        # Given a string `ms` of type 'VKR940095', locate the corresponding
        # movement.
        dd.logger.info("Resolving %d matches", len(self.must_match))
        for ms, lst in self.must_match.items():
            for (voucher, matching) in lst:
                if matching.pk is None:
                    dd.logger.warning("Ignored match %s in %s (pk is None)" % (
                        ms, matching))
                    continue
                idjnl, iddoc = ms[:3], ms[3:]
                try:
                    year, num = year_num(iddoc)
                except ValueError as e:
                    dd.logger.warning("Ignored match %s in %s (%s)" % (
                        ms, matching, e))
                try:
                    jnl = Journal.objects.get(ref=idjnl)
                except Journal.DoesNotExist:
                    dd.logger.warning("Ignored match %s in %s (invalid JNL)" % (
                        ms, matching))
                    continue
                qs = Movement.objects.filter(
                    voucher__journal=jnl, voucher__number=num,
                    voucher__year=year, partner__isnull=False)
                if qs.count() == 0:
                    dd.logger.warning("Ignored match %s in %s (no movement)" % (
                        ms, matching))
                    continue
                matching.match = qs[0]
                matching.save()
                voucher.deregister(ses)
                voucher.register(ses)
                
        

    def par_class(self, row):
        # wer eine nationalregisternummer hat ist eine Person, selbst wenn er
        # auch eine MwSt-Nummer hat.
        if True:  # must convert them manually
            return rt.modules.contacts.Company
        prt = row.idprt
        if prt == 'O':
            return rt.modules.contacts.Company
        elif prt == 'L':
            return rt.modules.lists.List
        elif prt == 'P':
            return rt.modules.contacts.Person
        elif prt == 'F':
            return rt.modules.households.Household
        # dd.logger.warning("Unhandled PAR->IdPrt %r",prt)

    def dc2lino(self, dc):
        if dc == "D":
            return rt.modules.accounts.DEBIT
        elif dc == "C":
            return rt.modules.accounts.CREDIT
        elif dc == "A":
            return rt.modules.accounts.DEBIT
        elif dc == "E":
            return rt.modules.accounts.CREDIT
        raise Exception("Invalid D/C value %r" % dc)

    def create_users(self):
        pass

    def dbfmemo(self, s):
        s = s.replace('\r\n', '\n')
        s = s.replace(u'\xec\n', '')
        # s = s.replace(u'\r\nì',' ')
        if u'ì' in s:
            raise Exception("20121121 %r" % s)
        return s.strip()

    def after_gen_load(self):
        Account = rt.modules.accounts.Account
        sc = dict()
        for k, v in dd.plugins.tim2lino.siteconfig_accounts.items():
            sc[k] = Account.get_by_ref(v)
        settings.SITE.site_config.update(**sc)
        # func = dd.plugins.tim2lino.setup_tim2lino
        # if func:
        #     func(self)

    def decode_string(self, v):
        return v
        # return v.decode(self.codepage)

    def babel2kw(self, tim_fld, lino_fld, row, kw):
        if dd.plugins.tim2lino.use_dbf_py:
            import dbf
            ex = dbf.FieldMissingError
        else:
            ex = Exception
        for i, lng in enumerate(self.languages):
            try:
                v = getattr(row, tim_fld + str(i + 1), '').strip()
                if v:
                    v = self.decode_string(v)
                    kw[lino_fld + lng.suffix] = v
                    if lino_fld not in kw:
                        kw[lino_fld] = v
            except ex as e:
                pass
                dd.logger.info("Ignoring %s", e)

    def load_jnl_alias(self, row, **kw):
        vcl = None
        if row.alias == 'VEN':
            vat = rt.modules.vat
            ledger = rt.modules.ledger
            sales = rt.modules.sales
            if row.idctr == 'V':
                kw.update(trade_type=vat.TradeTypes.sales)
                kw.update(journal_group=ledger.JournalGroups.sales)
                vcl = sales.VatProductInvoice
            elif row.idctr == 'E':
                kw.update(trade_type=vat.TradeTypes.purchases)
                vcl = vat.VatAccountInvoice
                kw.update(journal_group=ledger.JournalGroups.purchases)
            else:
                raise Exception("Invalid JNL->IdCtr '{0}'".format(row.idctr))
        elif row.alias == 'FIN':
            finan = rt.modules.finan
            ledger = rt.modules.ledger
            accounts = rt.modules.accounts
            idgen = row.idgen.strip()
            kw.update(journal_group=ledger.JournalGroups.financial)
            if idgen:
                kw.update(account=accounts.Account.get_by_ref(idgen))
                if idgen.startswith('58'):
                    kw.update(trade_type=vat.TradeTypes.purchases)
                    vcl = finan.PaymentOrder
                elif idgen.startswith('5'):
                    vcl = finan.BankStatement
            else:
                vcl = finan.JournalEntry
        # if vcl is None:
        #     raise Exception("Journal type not recognized: %s" % row.idjnl)
        return vcl, kw
        
    def load_jnl(self, row, **kw):
        vcl = None
        kw.update(ref=row.idjnl.strip(), name=row.libell)
        kw.update(dc=self.dc2lino(row.dc))
        # kw.update(seqno=self.seq2lino(row.seq.strip()))
        kw.update(seqno=int(row.seq.strip()))
        # kw.update(seqno=row.recno())
        kw.update(auto_check_clearings=False)
        vcl, kw = self.load_jnl_alias(row, **kw)
        if vcl is not None:
            return vcl.create_journal(**kw)

    def load_dbf(self, tableName, row2obj=None):
        if row2obj is None:
            row2obj = getattr(self, 'load_' + tableName[-3:].lower())
        fn = self.dbpath
        if self.archive_name is not None:
            if tableName in self.archived_tables:
                fn = os.path.join(fn, self.archive_name)
        fn = os.path.join(fn, tableName)
        fn += dd.plugins.tim2lino.dbf_table_ext
        if dd.plugins.tim2lino.use_dbf_py:
            dd.logger.info("Loading %s...", fn)
            import dbf  # http://pypi.python.org/pypi/dbf/
            # table = dbf.Table(fn)
            table = dbf.Table(fn, codepage=self.codepage)
            # table.use_deleted = False
            table.open()
            # print table.structure()
            dd.logger.info("Loading %d records from %s (%s)...",
                           len(table), fn, table.codepage)
            for record in table:
                if not dbf.is_deleted(record):
                    try:
                        yield row2obj(record)
                    except Exception as e:
                        dd.logger.warning(
                            "Failed to load record %s from %s : %s",
                            record, tableName, e)

                    # i = row2obj(record)
                    # if i is not None:
                    #     yield settings.TIM2LINO_LOCAL(tableName, i)
            table.close()
        elif dd.plugins.tim2lino.use_dbfread:
            dd.logger.info("Loading readonly %s...", fn)
            from dbfread import DBF
            dbf = DBF(fn)
            for record in dbf:
                d = { f.name.lower() : record[f.name] for f in dbf.fields}
                d = AttrDict(d)
                try:
                    yield row2obj(d)
                except Exception as e:
                    dd.logger.warning(
                        "Failed to load record %s from %s : %s",
                        record, tableName, e)

        else:
            f = dbfreader.DBFFile(fn, codepage="cp850")
            dd.logger.info("Loading %d records from %s...", len(f), fn)
            f.open(deleted=True)
            # must set deleted=True and then filter them out myself
            # because big tables can raise
            # RuntimeError: maximum recursion depth exceeded in cmp
            for dbfrow in f:
                if not dbfrow.deleted():
                    try:
                        i = row2obj(dbfrow)
                        if i is not None:
                            yield settings.TIM2LINO_LOCAL(tableName, i)
                    except Exception as e:
                        traceback.print_exc(e)
                        dd.logger.warning("Failed to load record %s : %s",
                                          dbfrow, e)
            f.close()

        self.after_load(tableName)

    def after_load(self, tableName):
        for tableName2, func in dd.plugins.tim2lino.load_listeners:
            if tableName2 == tableName:
                func(self)

