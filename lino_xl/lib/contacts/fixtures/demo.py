# -*- coding: UTF-8 -*-
# Copyright 2009-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str
import six

from django.conf import settings
from lino.utils.instantiator import Instantiator
from lino.utils import Cycler
from lino.api import dd, rt

from lino.utils.demonames.bel import streets_of_eupen
STREETS = Cycler(streets_of_eupen())
Place = rt.models.countries.Place

def site_company_objects():

    company = Instantiator(
        'contacts.Company',
        "name zip_code city:name street street_no",
        country='EE').build
    rumma = company(
        'Rumma & Ko OÜ', '78003', 'Vigala', 'Uus tn', '1',
        url="http://www.saffre-rumma.net/")
    if dd.is_installed('vat'):
        rumma.vat_id = "EE100588749"
        # a vat_id is required for generating valid XML from payment order
    yield rumma

    settings.SITE.site_config.update(site_company=rumma)


def lookup_city(name):
    flt = rt.lookup_filter('name', name)
    try:
        return Place.objects.get(flt)
    except Place.MultipleObjectsReturned:
        raise Exception("20190406 Multiple cities {} for {} : {}".format(
            name, flt, Place.objects.filter(flt)))
    except Place.DoesNotExist:
        # city = Place.objects.get(name=name)
        raise Exception("20190406 City {} not found in {} ({})".format(
            name, Place.objects.all(), flt))
        return


def person(city, first_name, last_name, **kwargs):
    if isinstance(city, six.string_types):
        city = lookup_city(city)
    if city is None:
        return
    kwargs.update(
        country=city.country, city=city,
        first_name=first_name, last_name=last_name)
    return rt.models.contacts.Person(**kwargs)


def company(name, zip_code, city, street, street_no):
    if isinstance(city, six.string_types):
        city = lookup_city(city)
    if city is None:
        return
    kwargs = dict(
        country=city.country, name=name, zip_code=zip_code,
        city=city, street=street, street_no=street_no)
    return rt.models.contacts.Company(**kwargs)
    # if dd.is_installed('vat'):
    #     rt.models.vat.init_demo_company(obj)
    # return obj


def objects():

    yield site_company_objects()

    aachen = lookup_city('Aachen')
    eupen = lookup_city('Eupen')
    raeren = lookup_city('Raeren')
    angleur = lookup_city('Angleur')
    paris = lookup_city('Paris')
    amsterdam = lookup_city('Amsterdam')

    # company = Instantiator(
    #     'contacts.Company', "name zip_code city:name street street_no",
    #     country='BE').build
    yield company('Bäckerei Ausdemwald', '4700', eupen,
                  'Vervierser Straße', '45')
    yield company('Bäckerei Mießen',     '4700', eupen,
                  'Gospert', '103')
    yield company('Bäckerei Schmitz',    '4700', eupen,
                  'Aachener Straße', '53')
    yield company('Garage Mergelsberg',  '4730', raeren,
                  'Hauptstraße', '13')

    # company = Instantiator(
    #     'contacts.Company',
    #     "name zip_code city:name street street_no", country='NL').build
    yield company('Donderweer BV', '4816 AR', 'Breda', 'Edisonstraat', '12')
    yield company('Van Achter NV', '4836 LG', 'Breda', 'Hazeldonk', '2')

    # company = Instantiator(
    #     'contacts.Company',
    #     "name zip_code city:name street street_no", country='DE').build
    yield company('Hans Flott & Co', '22453', 'Hamburg',
                  'Niendorfer Weg', '532')
    yield company('Bernd Brechts Bücherladen', '80333',
                  aachen, 'Brienner Straße', '18')
    yield company('Reinhards Baumschule', '12487 ',
                  'Berlin', 'Segelfliegerdamm', '123')

    # company = Instantiator(
    #     'contacts.Company',
    #     "name zip_code city:name street street_no", country='FR').build
    yield company('Moulin Rouge', '75018', 'Paris',
                  'Boulevard de Clichy', '82')
    yield company('Auto École Verte', '54000 ', 'Nancy',
                  'rue de Mon Désert', '12')

    # person = Instantiator("contacts.Person", "first_name last_name",
    #                       country='BE', city=eupen, zip_code='4700').build
    yield person(eupen, 'Andreas',  'Arens', gender=dd.Genders.male,
                 phone="+32 87123456", email="andreas@arens.com")
    yield person(eupen, 'Annette',  'Arens', gender=dd.Genders.female,
                 phone="+32 87123457", email="annette@arens.com")
    yield person(eupen, 'Hans',     'Altenberg', gender=dd.Genders.male)
    yield person(eupen, 'Alfons',   'Ausdemwald', gender=dd.Genders.male)
    yield person(eupen, 'Laurent',  'Bastiaensen', gender=dd.Genders.male)
    yield person(eupen, 'Charlotte', 'Collard', gender=dd.Genders.female)
    yield person(eupen, 'Ulrike',   'Charlier', gender=dd.Genders.female)
    yield person(eupen, 'Marc',  'Chantraine', gender=dd.Genders.male)
    yield person(eupen, 'Daniel',   'Dericum', gender=dd.Genders.male)
    yield person(eupen, 'Dorothée', 'Demeulenaere', gender=dd.Genders.female)
    yield person(eupen, 'Dorothée', 'Dobbelstein-Demeulenaere',
                 gender=dd.Genders.female)
    yield person(eupen, 'Dorothée', 'Dobbelstein', gender=dd.Genders.female)
    yield person(eupen, 'Berta',    'Ernst', gender=dd.Genders.female)
    yield person(eupen, 'Bernd',    'Evertz', gender=dd.Genders.male)
    yield person(eupen, 'Eberhart', 'Evers', gender=dd.Genders.male)
    yield person(eupen, 'Daniel',   'Emonts', gender=dd.Genders.male)
    yield person(eupen, 'Edgar',    'Engels', gender=dd.Genders.male)
    yield person(eupen, 'Luc',      'Faymonville', gender=dd.Genders.male)
    yield person(eupen, 'Germaine', 'Gernegroß', gender=dd.Genders.female)
    yield person(eupen, 'Gregory',  'Groteclaes', gender=dd.Genders.male)
    yield person(eupen, 'Hildegard', 'Hilgers', gender=dd.Genders.female)
    yield person(eupen, 'Henri',    'Hilgers', gender=dd.Genders.male)
    yield person(eupen, 'Irene',    'Ingels', gender=dd.Genders.female)
    yield person(eupen, 'Jérémy',   'Jansen', gender=dd.Genders.male)
    yield person(eupen, 'Jacqueline', 'Jacobs', gender=dd.Genders.female)
    yield person(eupen, 'Johann', 'Johnen', gender=dd.Genders.male)
    yield person(eupen, 'Josef', 'Jonas', gender=dd.Genders.male)
    yield person(eupen, 'Jan',   'Jousten', gender=dd.Genders.male)
    yield person(eupen, 'Karl',  'Kaivers', gender=dd.Genders.male)
    yield person(eupen, 'Guido', 'Lambertz', gender=dd.Genders.male)
    yield person(eupen, 'Laura', 'Laschet', gender=dd.Genders.female)
    yield person(eupen, 'Line', 'Lazarus', gender=dd.Genders.female)
    yield person(eupen, 'Josefine', 'Leffin', gender=dd.Genders.female)
    yield person(eupen, 'Marc', 'Malmendier', gender=dd.Genders.male)
    yield person(eupen, 'Melissa', 'Meessen', gender=dd.Genders.female)
    yield person(eupen, 'Michael', 'Mießen', gender=dd.Genders.male)
    yield person(eupen, 'Marie-Louise', 'Meier', gender=dd.Genders.female)

    # person = Instantiator(
    #     "contacts.Person", "first_name last_name",
    #     country='BE', language=settings.SITE.DEFAULT_LANGUAGE.django_code,
    #     city=raeren, zip_code='4730').build
    yield person(raeren, 'Erich',    'Emonts', gender=dd.Genders.male)
    yield person(raeren, 'Erwin',    'Emontspool', gender=dd.Genders.male)
    yield person(raeren, 'Erna',     'Emonts-Gast', gender=dd.Genders.female)
    yield person(raeren, 'Alfons',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Berta',     'Radermacher', gender=dd.Genders.female)
    yield person(raeren, 'Christian',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Daniela',     'Radermacher', gender=dd.Genders.female)
    yield person(raeren, 'Edgard',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Fritz',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Guido',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Hans',     'Radermacher', gender=dd.Genders.male)
    yield person(raeren, 'Hedi',     'Radermacher', gender=dd.Genders.female)
    yield person(raeren, 'Inge',     'Radermacher', gender=dd.Genders.female)
    yield person(raeren, 'Jean',     'Radermacher', gender=dd.Genders.male)

    # special challenges for alphabetic ordering
    yield person(raeren, 'Didier',  'di Rupo', gender=dd.Genders.male)
    yield person(raeren, 'David',   'da Vinci', gender=dd.Genders.male)
    yield person(raeren, 'Vincent', 'van Veen', gender=dd.Genders.male)
    yield person(raeren, 'Õie',     'Õunapuu', gender=dd.Genders.female)
    yield person(raeren, 'Otto',   'Östges', gender=dd.Genders.male)
    yield person(raeren, 'Erna',   'Ärgerlich', gender=dd.Genders.female)

    # person = Instantiator("contacts.Person", country='BE',
    #                       city=Place.objects.get(name__exact='Angleur')).build
    yield person(angleur, 'Bernard', 'Bodard', title='Dr.')
    yield person(angleur, 'Jean', 'Dupont')

    # person = Instantiator("contacts.Person", country='NL',
    #                       city=Place.objects.get(
    #                           name__exact='Amsterdam')).build
    yield person(amsterdam, 'Mark', 'Martelaer',
                 gender=dd.Genders.male)
    yield person(amsterdam, 'Rik', 'Radermecker',
                 gender=dd.Genders.male)
    yield person(amsterdam, 'Marie-Louise', 'Vandenmeulenbos',
                 gender=dd.Genders.female)

    # person = Instantiator("contacts.Person", country='DE').build
    yield person(aachen, 'Emil', 'Eierschal', gender=dd.Genders.male)
    yield person(aachen, 'Lisa', 'Lahm', gender=dd.Genders.female)
    yield person(aachen, 'Bernd', 'Brecht', gender=dd.Genders.male)
    yield person(aachen, 'Karl', 'Keller', gender=dd.Genders.male)

    # person = Instantiator("contacts.Person", country='FR').build
    yield person(paris, 'Robin', 'Dubois', gender=dd.Genders.male)
    yield person(paris, 'Denis', 'Denon', gender=dd.Genders.male)
    yield person(paris, 'Jérôme', 'Jeanémart', gender=dd.Genders.male)

    nr = 1
    for p in rt.models.contacts.Person.objects.filter(city=eupen):
        p.street = STREETS.pop()
        p.stret_no = str(nr)
        p.save()
        nr += 1
