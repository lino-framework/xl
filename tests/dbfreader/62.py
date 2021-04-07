#coding: latin1
# Copyright 2003-2009 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
discovering and extending Lars M. Garshol's dbfreader.py
"""
import os
import unittest
from cStringIO import StringIO
from lino.utils import dbfreader

dataPath = os.path.dirname(__file__)

class Case(unittest.TestCase):

    def test01(self):
        f = dbfreader.DBFFile(os.path.join(dataPath,"NAT.DBF"),
                              codepage="cp850")

        ae = self.assertEqual
        ae(f.get_version(),"dBASE III")
        ae(f.has_memo(),False)
        ae(str(f.lastUpdate),"2003-01-22")
        ae(f.get_record_count(),14)
        ae(f.get_record_len(),94)
        #print get_fields(f)
        ae(get_fields(f),"""\
IDNAT: Character (3)
NAME: Character (40)
INTRA: Character (3)
IDLNG: Character (1)
IDTLF: Character (1)
TELPREFIX: Character (6)
TVAPREFIX: Character (3)
IDDEV: Character (3)
TVAPICT: Character (25)
ATTRIB: Character (5)
IDREG: Character (1)
ISOCODE: Character (2)""")

        s = "\n".join([rec["NAME"].strip() for rec in f.fetchall()])
        #print s
        ae(s,u"""\
Belgien
Luxemburg
Deutschland
Niederlande
Frankreich
Gro�britannien
Italien
Irland
Spanien
Portugal
Schweiz
�sterreich
D�nemark
United States of America""")


    def test02(self):
        f = dbfreader.DBFFile(os.path.join(dataPath,"PAR.DBF"),
                              codepage="cp850")

        ae = self.assertEqual
        ae(f.has_memo(),True)
        ae(f.get_version(),"dBASE III+ with memo")
        ae(f.get_record_count(),48)
        ae(f.get_record_len(),879)
        s = get_fields(f)
        ae(s,"""\
IDPAR: Character (6)
IDGEN: Character (6)
FIRME: Character (35)
NAME2: Character (35)
RUE: Character (35)
CP: Character (8)
IDPRT: Character (1)
PAYS: Character (3)
TEL: Character (18)
FAX: Character (18)
COMPTE1: Character (47)
NOTVA: Character (18)
COMPTE3: Character (47)
IDPGP: Character (2)
DC.debit: Character (10)
DC.credit: Character (10)
ATTRIB: Character (5)
IDMFC: Character (3)
LANGUE: Character (1)
PROF: Character (4)
CODE1: Character (12)
CODE2: Character (12)
CODE3: Character (12)
DATCREA: Date (8)
IDREG: Character (1)
ALLO: Character (35)
NB1: Character (60)
NB2: Character (60)
IDDEV: Character (3)
MEMO: Memo field (10)
COMPTE2: Character (47)
RUENUM: Character (4)
RUEBTE: Character (6)
MVPDATE: Date (8)
VORNAME: Character (20)
EMAIL: Character (250)
GSM: Character (18)""")
        fmt = "|%(IDPAR)s|%(FIRME)s|"
        rows = f.fetchall()
        s = "\n".join([fmt % rec for rec in rows[10:15]])
        #print s
        ae(s,u"""\
|000008|Ausdemwald|
|000012|M�ller AG|
|000013|Bodard|
|000014|Mendelssohn GmbH|
|000015|INTERMOBIL s.a.|""")

        norbert = rows[10]
        ae(norbert['FIRME'].strip(),"Ausdemwald")
        ae(norbert['IDPAR'],"000008")
        ae(norbert['MEMO'],u"""\
Das ist der Memotext zu Norbert Ausdemwald (IdPar 000008).
Hier ist eine zweite Zeile.

Auf der vierten Zeile kommen weiche Zeilenspr�nge (ASCII 141) hinzu, die von memoedit() automatisch eingef�gt werden, wenn eine Zeile l�nger als der Texteditor ist. Hinter "von" und "der" m�sste jeweils ein ASCII 141 sein.
Und jetzt ist Schluss. Ohne Leerzeile hinter dem Ausrufezeichen!""")



def get_fields(f):
    return "\n".join( ["%s: %s (%d)" % (field.get_name(),
                                        field.get_type_name(),
                                        field.get_len())
                       for field in f.get_fields()])

if __name__ == "__main__":
    unittest.main()
