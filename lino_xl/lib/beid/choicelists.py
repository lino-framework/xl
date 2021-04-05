# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


class ResidenceTypes(dd.ChoiceList):
    verbose_name = _("Resident register")
    verbose_name_plural = _("Resident registers")

add = ResidenceTypes.add_item
add('1', _("Register of citizens"))
add('2', _("Register of foreigners"))
add('3', _("Waiting register"))


class BeIdCardTypes(dd.ChoiceList):

    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("eID card type")
    verbose_name_plural = _("eID card types")
    old2new = {'1' : '01', '6': '06'}

add = BeIdCardTypes.add_item
# add('1', _("Belgian citizen"), "belgian_citizen")
add('01', _("Belgian citizen"), "belgian_citizen")
# ,de=u"Belgischer Staatsbürger",fr=u"Citoyen belge"),
add('06', _("Kids card (< 12 year)"), "kids_card")
#add('06', _("Kids card (< 12 year)"), "kids_card0")
#,de=u"Kind unter 12 Jahren"),

#~ add('8', _("Habilitation"))
#,fr=u"Habilitation",nl=u"Machtiging")

add('11', _("Foreigner card A"), "foreigner_a")
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister - Tijdelijk verblijf",
        #~ fr=u"Certificat d'inscription au registre des étrangers - Séjour temporaire",
        #~ de=u"Ausländerkarte A Bescheinigung der Eintragung im Ausländerregister - Vorübergehender Aufenthalt",
add('12', _("Foreigner card B"), "foreigner_b")
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister",
        #~ fr=u"Certificat d'inscription au registre des étrangers",
        #~ de=u"Ausländerkarte B (Bescheinigung der Eintragung im Ausländerregister)",
add('13', _("Foreigner card C"), "foreigner_c")
        #~ nl=u"Identiteitskaart voor vreemdeling",
        #~ fr=u"Carte d'identité d'étranger",
        #~ de=u"C (Personalausweis für Ausländer)",
add('14', _("Foreigner card D"), "foreigner_d")
        #~ nl=u"EG - langdurig ingezetene",
        #~ fr=u"Résident de longue durée - CE",
        #~ de=u"Daueraufenthalt - EG",
add('15', _("Foreigner card E"), "foreigner_e")
        #~ nl=u"Verklaring van inschrijving",
        #~ fr=u"Attestation d’enregistrement",
        #~ de=u"Anmeldebescheinigung",
add('16', _("Foreigner card E+"), "foreigner_e_plus")
        # Document ter staving van duurzaam verblijf van een EU onderdaan
add('17', _("Foreigner card F"), "foreigner_f")
        #~ nl=u"Verblijfskaart van een familielid van een burger van de Unie",
        #~ fr=u"Carte de séjour de membre de la famille d’un citoyen de l’Union",
        #~ de=u"Aufenthaltskarte für Familienangehörige eines Unionsbürgers",
add('18', _("Foreigner card F+"), "foreigner_f_plus")

# This is not an electronic card, but it makes sense to add it to this
# list e.g. for Lino Avanti:
# FR: Attestation d’immatriculation (Carte orange)
# DE: Eintragungsbescheinigung (Orange Karte)
add('99', _("Registration certificate (Orange card)"), "orange_card")
