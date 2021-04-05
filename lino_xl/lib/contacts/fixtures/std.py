# -*- coding: UTF-8 -*-
# Copyright 2009-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from builtins import filter

from django.db import models
from django.conf import settings

from lino.api import dd, rt, _
from lino.api.dd import babel_values

from lino.core.utils import resolve_model
from lino.utils.instantiator import Instantiator

companyType = Instantiator('contacts.CompanyType', "abbr name").build
roletype = Instantiator('contacts.RoleType', "name").build

# thanks to http://belgium.angloinfo.com/countries/belgium/businesses.asp
# see also http://en.wikipedia.org/wiki/Types_of_business_entity

COMPANY_TYPES_FORMAT = 'en nl fr de'
COMPANY_TYPES_TEXT = u"""
Public Limited Company    | NV (Naamloze Vennootschap)   | SA (Société Anonyme) |  AG (Aktiengesellschaft)
Limited Liability Company | BVBA (Besloten Vennootschap met Beperkte Aansprakelijkheid)  | SPRL (Société Privée à Responsabilité Limitée) | PGmbH (Private Gesellschaft mit beschränkter Haft)
One-person Private Limited Company | EBVBA (Eenpersoons Beslotenvennootschap met Beperkte Aansprakelijkheid) | SPRLU (Société d'Une Personne à Responsabilité Limitée) | EGmbH (Einpersonengesellschaft mit beschränkter Haft)
Cooperative Company with Limited Liability | CVBA (Cooperatieve Vennootschap met Beperkte Aansprakelijkheid) | SCRL (Société Coopérative à Responsabilité Limitée) | Kooperative mit beschränkter Haft
Cooperative Company with Unlimited Liability | CVOA (Cooperatieve Vennootschap met Onbeperkte Aansprakelijkheid) | SCRI (Société Coopérative à Responsabilité Illimitée) | Kooperative mit unbeschränkter Haft
General Partnership | Comm VA (Commanditaire Vennootschap op Aandelen | SNC (Société en Nom Collectif) |
Limited Partnership | Comm V (Gewone Commanditaire Vennootschap) | SCS (Société en Commandite Simple) |
Non-stock Corporation | Maatschap | Société de Droit Commun | Gesellschaft öffentlichen Rechts
Charity/Company established for social purposes | VZW (Vereniging Zonder Winstoogmerk) | ASBL (Association sans But Lucratif) | V.o.G. (Vereinigung ohne Gewinnabsicht)

Cooperative Company | CV (Cooperatieve Vennootschap) | SC (Société Coopérative) | Genossenschaft
Company | Firma | Société | Firma
Public service |  | Service Public | Öffentlicher Dienst
Ministry |  | Ministère | Ministerium
School |  | école | Schule
Freelancer | Freelacer | Travailleur libre | Freier Mitarbeiter
Sole proprietorship | Eenmanszaak | Entreprise individuelle | Einzelunternehmen
"""
COMPANY_TYPES = []


def parse(s):
    a = s.split("(", 1)
    if len(a) == 2:
        name = a[1].strip()
        if name.endswith(")"):
            return dict(abbr=a[0].strip(), name=name[:-1])
    s = s.strip()
    if not s:
        return {}
    return dict(name=s)

LANGS = {}

for i, lang in enumerate(COMPANY_TYPES_FORMAT.split()):
    li = settings.SITE.get_language_info(lang)
    if li is not None:
        LANGS[li.index] = i

#~ print LANGS

for ln in COMPANY_TYPES_TEXT.splitlines():
    if ln and ln[0] != "#":
        a = ln.split('|')
        if len(a) != 4:
            raise Exception("Line %r has %d fields (expected 4)" % len(a))
        d = dict()
        for index, i in LANGS.items():
            kw = parse(a[i])
            if index == 0:
                d.update(kw)
            else:
                for k, v in kw.items():
                    d[k + settings.SITE.languages[index].suffix] = v

        def not_empty(x):
            return x
        #~ print d
        if 'name' in d:
            # if there's at least one non-empty value
            if list(filter(not_empty, list(d.values()))):
                COMPANY_TYPES.append(d)


def objects():

    Partner = rt.models.contacts.Partner
    Person = rt.models.contacts.Person

    for ct in COMPANY_TYPES:
        yield companyType(**ct)

    # qs = rt.models.contacts.RoleType.objects.filter(rt.lookup_filter('name', "CEO"))
    # if qs.count():
    #     raise Exception("Oops, there is already a CEO in {}".format(qs))
    # dd.logger.info("Creating the CEO function")
    yield roletype(**dd.str2kw('name', _("CEO"), can_sign=True))
    yield roletype(**dd.str2kw('name', _("Director"), can_sign=True))
    yield roletype(**dd.str2kw('name', _("Secretary")))
    yield roletype(**dd.str2kw('name', _("IT manager")))
    yield roletype(**dd.str2kw('name', _("President"), can_sign=True))
    # yield roletype(**babel_values('name', en="Manager", fr='Gérant', de="Geschäftsführer", et="Tegevjuht"))
    # yield roletype(**babel_values('name', en="Director", fr='Directeur', de="Direktor", et="Direktor"))
    # yield roletype(**babel_values('name', en="Secretary", fr='Secrétaire', de="Sekretär", et="Sekretär"))
    # yield roletype(**babel_values('name', en="IT Manager", fr='Gérant informatique', de="EDV-Manager", et="IT manager"))
    # yield roletype(**babel_values('name', en="President", fr='Président', de="Präsident", et="President"))


    if dd.is_installed('excerpts') and dd.is_installed('appypod'):
        ExcerptType = rt.models.excerpts.ExcerptType
        ContentType = rt.models.contenttypes.ContentType
        yield ExcerptType(
            build_method='appypdf',
            template="TermsConditions.odt",
            content_type=ContentType.objects.get_for_model(Person),
            **dd.str2kw('name', _("Terms & conditions")))

    if dd.is_installed('contenttypes'):
        # TODO: remove this because the feature isn't used. But afterwards adapt
        # the doctests!
        ContentType = rt.models.contenttypes.ContentType
        I = Instantiator('gfks.HelpText',
                         'content_type field help_text').build
        t = ContentType.objects.get_for_model(Person)

        #~ yield I(t,'birth_date',u"""\
    #~ Unkomplette Geburtsdaten sind erlaubt, z.B.
    #~ <ul>
    #~ <li>00.00.1980 : irgendwann in 1980</li>
    #~ <li>00.07.1980 : im Juli 1980</li>
    #~ <li>23.07.0000 : Geburtstag am 23. Juli, Alter unbekannt</li>
    #~ </ul>
    #~ """)

        ct = ContentType.objects.get_for_model(Partner)
        yield I(ct, 'language', u"""\
    Die Sprache, in der Dokumente ausgestellt werden sollen.
    """)
