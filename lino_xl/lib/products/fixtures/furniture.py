# -*- coding: UTF-8 -*-
# Copyright 2009-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.utils.instantiator import Instantiator
from lino_xl.lib.products.choicelists import ProductTypes

from lino.api import dd, _


def objects():

    productcat = Instantiator('products.Category').build
    product = Instantiator('products.Product', "sales_price category").build

    furniture = productcat(
        id=1, product_type=ProductTypes.default, **dd.babel_values(
            'name', _("Furniture"), et="Mööbel", de="Möbel", fr="Meubles"))
    yield furniture
    # print "foo", furniture.id, furniture
    hosting = productcat(
        id=2, product_type=ProductTypes.default, **dd.babel_values(
            'name', _("Website Hosting"),
            et="Veebimajutus",
            de="Website-Hosting",
            fr="Hébergement de sites Internet"))
    yield hosting

    other = productcat(id=3, **dd.str2kw('name', _("Other")))
    yield other

    kw = dd.babel_values('name', _("Wooden table"),
                      et=u"Laud puidust",
                      de="Tisch aus Holz",
                      fr=u"Table en bois")
    kw.update(dd.babel_values(
        'description', _("""\
This table is made of pure wood.
It has **four legs**.
Designed to fit perfectly with **up to 6 wooden chairs**.
Product of the year 2008."""),
        et="""\
See laud on tehtud ehtsast puust.
Sellel on **neli jalga**.
Disainitud sobida kokku **kuni 6 puidust tooliga**.
Product of the year 2008.""",
        de="""\
Dieser Tisch ist aus echtem Holz.
Er hat **vier Beine**.
Passt perfekt zusammen mit **bis zu 6 Stühlen aus Holz**.
Produkt des Jahres 2008.""",
        fr="""\
Cette table est en bois authentique.
Elle a **quatre jambes**.
Conçue pour mettre jusqu'à **6 chaises en bois**.
Produit de l'année 2008.""",
    ))
    yield product("199.99", 1, **kw)
    yield product("99.99", 1, **dd.babel_values('name', _("Wooden chair"),
                                             et="Tool puidust",
                                             de="Stuhl aus Holz",
                                             fr="Chaise en bois"))
    yield product("129.99", 1, **dd.babel_values('name', _("Metal table"),
                                              et="Laud metallist",
                                              de="Tisch aus Metall",
                                              fr="Table en métal"))
    yield product("79.99", 1, **dd.babel_values('name', _("Metal chair"),
                                             et="Tool metallist",
                                             de="Stuhl aus Metall",
                                             fr="Chaise en métal"))
    hosting = product("3.99", 2,
                      **dd.babel_values('name', _("Website hosting 1MB/month"),
                                     et="Majutus 1MB/s",
                                     de="Website-Hosting 1MB/Monat",
                                     fr="Hébergement 1MB/mois"))
    yield hosting
    yield product("30.00", 2,
                  **dd.babel_values('name', _("IT consultation & maintenance"),
                                 et=u"IKT konsultatsioonid & hooldustööd",
                                 de=u"EDV Konsultierung & Unterhaltsarbeiten",
                                 fr=u"ICT Consultation & maintenance"))
    yield product("35.00", 2, **dd.babel_values(
        'name', _("Server software installation, configuration and administration"),
        et="Serveritarkvara installeerimine, seadistamine ja administreerimine",
        de="Server software installation, configuration and administration",
        fr="Server software installation, configuration and administration"))

    yield product("40.00", 2, **dd.babel_values(
        'name', _("Programming"),
        et="Programmeerimistööd",
        de="Programmierung",
        fr="Programmation"))

    yield product("25.00", 2, **dd.babel_values(
        'name', _("Image processing and website content maintenance"),
        et="Pilditöötlus ja kodulehtede sisuhaldustööd",
        de="Bildbearbeitung und Unterhalt Website",
        fr="Traitement d'images et maintenance site existant"))

    yield product("29.90", 3, **dd.str2kw('name', _("Book"), vat_class="reduced"))
    yield product("1.40", 3, **dd.str2kw('name', _("Stamp"), vat_class="exempt"))
