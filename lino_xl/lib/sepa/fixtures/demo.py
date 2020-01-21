# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.utils.instantiator import Instantiator
from lino.api import rt, dd


Company = Instantiator('contacts.Company', 'name url').build
Account = Instantiator('sepa.Account', 'partner bic iban remark').build

# from lino_xl.lib.vat.choicelists import VatRegimes

class Adder(object):
    def __init__(self):
        self.current_partner = None
        self.primary = False
        # make the first account of every company primary

    def add_company(self, name, url, **kw):
        if not dd.is_installed('vat'):
            kw.pop('vat_id', None)
        obj = Company(name=name, url=url, **kw)
        # if VatRegimes.is_installed():
        # if dd.is_installed('bevats') or dd.is_installed('bevat'):
        #     if obj.country.isocode == 'BE':
        #         obj.vat_regime = VatRegimes.subject
        #     else:
        #         obj.vat_regime = VatRegimes.intracom
        self.current_partner = obj
        self.primary = True
        # if dd.is_installed('vat') and obj.vat_id:
        #     if obj.vat_id[:2] == obj.country.iso_code:
        #         obj.vat_regime = rt.models.vat.VatRegimes.subject
        #     else:
        #         obj.vat_regime = rt.models.vat.VatRegimes.intracom
        return obj

    def add_account(self, bic, iban, remark=''):
        iban = iban.replace(' ', '')
        acc = Account(
            self.current_partner, bic, iban, remark, primary=self.primary)
        self.primary = False
        return acc


def objects():
    adder = Adder()
    C = adder.add_company
    A = adder.add_account
    tallinn = rt.models.countries.Place.objects.get(name="Tallinn")

    yield C('AS Express Post', 'http://www.expresspost.ee/',
            country="EE", vat_id="EE100041561",
            street="Peterburi tee", street_no="34", street_box="/5",
            city=tallinn, zip_code="11415")
    yield A('HABAEE2X', 'EE872200221012067904')

    yield C('AS Matsalu Veevärk', 'http://www.matsaluvv.ee',
            country="EE", vat_id="EE100920666")
    yield A('HABAEE2X', 'EE732200221045112758')

    yield C('Eesti Energia AS', "http://www.energia.ee",
            country="EE", vat_id="EE100366327")
    yield A('HABAEE2X', 'EE232200001180005555', "Eraklilendile")
    yield A('HABAEE2X', 'EE322200221112223334', "Ärikliendile")
    yield A('EEUHEE2X', 'EE081010002059413005')
    yield A('FOREEE2X', 'EE70 3300 3320 9900 0006')
    yield A('NDEAEE2X', 'EE43 17000 1700 0115 797')

    yield C('IIZI kindlustusmaakler AS', "http://www.iizi.ee",
            country="EE", vat_id="EE100598027")
    yield A('HABAEE2X', 'EE382200221013987931')

    yield C('Maksu- ja Tolliamet', "http://www.emta.ee",
            street="Lõõtsa 8a",
            country="EE", zip_code="15176", city=tallinn)
            # needed by eevat payments fixture
    yield A('HABAEE2X', 'EE522200221013264447')

    yield C('Ragn-Sells AS', "http://www.ragnsells.ee", country="EE",
            street="Suur-Sõjamäe", street_no=50, street_box="a",
            zip_code="11415",
            city=tallinn, vat_id="EE100167089")
    yield A('HABAEE2X', 'EE202200221001178338')
    yield A('', 'EE781010220002715011 ')
    yield A('', 'EE321700017000231134')

    yield C('Electrabel Customer Solutions',
            "https://www.electrabel.be",
            country="BE",
            zip_code="1000",
            # city="Bruxelles",
            vat_id='BE 0476 306 127',
            street="Boulevard Simón Bolívar",
            street_no=34)
    # 1000 Bruxelles
    yield A('BPOTBEB1', 'BE46 0003 2544 8336')
    yield A('BPOTBEB1', 'BE81 0003 2587 3924')

    yield C('Ethias s.a.', "http://www.ethias.be",
            vat_id="BE 0404.484.654",
            street="Rue des Croisiers",
            street_no=24,
            country="BE",
            zip_code="4000")
    yield A('ETHIBEBB', 'BE79827081803833')

    yield C("Niederau Eupen AG", "http://www.niederau.be",
            vat_id="BE 0419.897.855",
            street="Herbesthaler Straße",
            street_no=134,
            country="BE",
            zip_code="4700")
    yield A('BBRUBEBB', 'BE98 3480 3103 3293')

    yield C("Leffin Electronics", "",
            email="info@leffin-electronics.be",
            vat_id="BE 0650.238.114",
            street="Schilsweg",
            street_no=80,
            country="BE",
            zip_code="4700")
    yield A('GEBABEBB', 'BE38 2480 1735 7572')
