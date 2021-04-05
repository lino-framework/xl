# -*- coding: UTF-8 -*-
# Copyright 2009-2018 Luc Saffre
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Import legacy data from TIM (basic version).
"""

import traceback
import os
from clint.textui import puts, progress
from django.conf import settings
from django.db import models
from lino.utils import AttrDict
from lino.api import dd, rt
from lino.utils import dbfreader
from lino_xl.lib.ledger.utils import DC


class TimLoader(object):

    LEN_IDGEN = 6
    ROOT  = None

    archived_tables = set()
    archive_name = None
    codepage = 'cp850'
    # codepage = 'cp437'
    # etat_registered = "C"¹
    etat_registered = u"¹"

    def __init__(self, dbpath, languages=None, **kwargs):
        self.dbpath = dbpath
        self.VENDICT = dict()
        self.FINDICT = dict()
        self.GROUPS = dict()
        self.languages = dd.resolve_languages(
            languages or dd.plugins.tim2lino.languages)
        self.must_register = []
        self.must_match = {}
        self.duplicate_zip_codes = dict()
        for k, v in kwargs.items():
            assert hasattr(self, k)
            setattr(self, k, v)

    def finalize(self):
        if len(self.duplicate_zip_codes):
            for country, codes in self.duplicate_zip_codes.items():
                dd.logger.warning(
                    "%d duplicate zip codes in %s : %s",
                    len(codes), country, ', '.join(codes))

        if self.ROOT is None:
            return
        
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
            return rt.models.contacts.Company
        prt = row.idprt
        if prt == 'O':
            return rt.models.contacts.Company
        elif prt == 'L':
            return rt.models.lists.List
        elif prt == 'P':
            return rt.models.contacts.Person
        elif prt == 'F':
            return rt.models.households.Household
        # dd.logger.warning("Unhandled PAR->IdPrt %r",prt)

    def dc2lino(self, dc):
        if dc == "D":
            return DC.debit
        elif dc == "C":
            return DC.credit
        elif dc == "A":
            return DC.debit
        elif dc == "E":
            return DC.credit
        raise Exception("Invalid D/C value %r" % dc)

    def create_users(self):
        pass

    def dbfmemo(self, s):
        if s is None:
            return ''
        s = s.replace('\r\n', '\n')
        s = s.replace(u'\xec\n', '')
        # s = s.replace(u'\r\nì',' ')
        # if u'ì' in s:
        #     raise Exception("20121121 %r contains \\xec" % s)
        # it might be at the end of the string:
        s = s.replace(u'ì','')
        return s.strip()

    def after_gen_load(self):
        return
        Account = rt.models.ledger.Account
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
            vat = rt.models.vat
            ledger = rt.models.ledger
            sales = rt.models.sales
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
            vat = rt.models.vat
            finan = rt.models.finan
            ledger = rt.models.ledger
            idgen = row.idgen.strip()
            kw.update(journal_group=ledger.JournalGroups.financial)
            if idgen:
                kw.update(account=ledger.Account.get_by_ref(idgen))
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
        count = 0
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
                        count += 1
                    except Exception as e:
                        traceback.print_exc()
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
                    count += 1
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
                            count += 1
                    except Exception as e:
                        traceback.print_exc()
                        dd.logger.warning(
                            "Failed to load record %s : %s", dbfrow, e)
            f.close()

        dd.logger.info(
            "{} rows have been loaded from {}.".format(count, fn))
        self.after_load(tableName)

    def after_load(self, tableName):
        for tableName2, func in dd.plugins.tim2lino.load_listeners:
            if tableName2 == tableName:
                func(self)



    def expand(self, obj):
        if obj is None:
            pass  # ignore None values
        elif isinstance(obj, models.Model):
            yield obj
        elif hasattr(obj, '__iter__'):
            for o in obj:
                for so in self.expand(o):
                    yield so
        else:
            dd.logger.warning("Ignored unknown object %r", obj)


    def objects(self):
        "Override this by subclasses."
        return []
    
    @classmethod
    def run(cls):
        """To be used when running this loader from a run script.

        Usage example:: 

            from lino_xl.lib.tim2lino.spzloader2 import TimLoader
            TimLoader.run()
        
        """
        self = cls(settings.SITE.legacy_data_path)
        counts = {}
        for o in self.expand(self.objects()):
            c = counts.setdefault(o.__class__, [0, 0])
            try:
                o.full_clean()
                o.save()
                c[0] += 1
            except Exception as e:
                c[1] += 1
                dd.logger.warning(
                    "Failed to save %s : %s", dd.obj2str(o), e)
                
            # temporary:
            # dd.logger.info("Saved %s", dd.obj2str(o))
        self.finalize()
        if counts:
            for m in sorted(counts.keys()):
                c = counts[m]
                dd.logger.info(
                    "%s : %d success, %d failed.", m, c[0], c[1])
        else:
            dd.logger.info("No objects have been imported.")
        
        
    
