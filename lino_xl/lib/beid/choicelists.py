# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


from lino.api import dd, _


class CivilStates(dd.ChoiceList):
    """The global list of **civil states** that a client can have.  This
    is the list of choices for the :attr:`civil_state
    <lino_welfare.modlib.pcsw.models.Client.civil_state>` field of a
    :class:`Client <lino_welfare.modlib.pcsw.models.Client>`.

    **The four official civil states** according to Belgian law are:

    .. attribute:: single

        célibataire : vous n’avez pas de partenaire auquel vous êtes
        officiellement lié

    .. attribute:: married

        marié(e) : vous êtes légalement marié

    .. attribute:: widowed

        veuf (veuve) / Verwitwet : vous êtes légalement marié mais
        votre partenaire est décédé

    .. attribute:: divorced

        divorcé(e) (Geschieden) : votre mariage a été juridiquement dissolu

    **Some institutions define additional civil states** for people
    who are officially still married but at different degrees of
    separation:

    .. attribute:: de_facto_separated

        De facto separated (Séparé de fait, faktisch getrennt)

        Des conjoints sont séparés de fait lorsqu'ils ne respectent
        plus le devoir de cohabitation. Leur mariage n'est cependant
        pas dissous.

        La notion de séparation de fait n'est pas définie par la
        loi. Toutefois, le droit en tient compte dans différents
        domaines, par exemple en matière fiscale ou en matière de
        sécurité sociale (assurance maladie invalidité, allocations
        familiales, chômage, pension, accidents du travail, maladies
        professionnelles).

    .. attribute:: separated

        Legally separated, aka "Separated as to property" (Séparé de
        corps et de biens, Getrennt von Tisch und Bett)

        La séparation de corps et de biens est une procédure
        judiciaire qui, sans dissoudre le mariage, réduit les droits
        et devoirs réciproques des conjoints.  Le devoir de
        cohabitation est supprimé.  Les biens sont séparés.  Les
        impôts sont perçus de la même manière que dans le cas d'un
        divorce. Cette procédure est devenue très rare.

    **Another unofficial civil state** (but relevant in certain
    situations) is:

    .. attribute:: cohabitating

        Cohabitating (cohabitant, zusammenlebend)

        Vous habitez avec votre partenaire et c’est
        reconnu légalement.

    Sources for above: `belgium.be
    <http://www.belgium.be/fr/famille/couple/divorce_et_separation/separation_de_fait/>`__,
    `gouv.qc.ca
    <http://www4.gouv.qc.ca/EN/Portail/Citoyens/Evenements/separation-divorce/Pages/separation-fait.aspx>`__,
    `wikipedia.org <https://en.wikipedia.org/wiki/Cohabitation>`__

    """
    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("Civil state")
    verbose_name_plural = _("Civil states")

    @classmethod
    def old2new(cls, old):
        """
        **Migration rules** (October 2015) to remove some obsolete choices:

        - 13 (Single cohabitating) becomes :attr:`cohabitating`
        - 18 (Single with child) becomes :attr:`single`
        - 21 (Married (living alone)) becomes :attr:`separated_de_facto`
        - 22 (Married (living with another partner)) becomes :attr:`separated_de_facto`
        - 33 (Widow cohabitating) becomes :attr:`widowed`

        """
        if old == '13':
            return cls.cohabitating
        if old == '18':
            return cls.single
        if old == '21':
            return cls.separated_de_facto
        if old == '22':
            return cls.separated_de_facto
        if old == '33':
            return cls.widowed
        return cls.get_by_value(old)

    @classmethod
    def to_python(cls, value):
        """This will call :meth:`old2new` when loading data from previous
        version. Can be removed when all production sites have been
        migrated.

        """
        if value:
            return cls.old2new(value)
        return None

add = CivilStates.add_item
add('10', _("Single"), 'single')
# add('13', _("Single cohabitating"))
# add('18', _("Single with child"))
add('20', _("Married"), 'married')
# add('21', _("Married (living alone)"))
# add('22', _("Married (living with another partner)"))
add('30', _("Widowed"), 'widowed')
# add('33', _("Widow cohabitating"))
add('40', _("Divorced"), 'divorced')
add('50', _("Separated"), 'separated')  # Getrennt von Tisch und Bett /
add('51', _("De facto separated"), 'separated_de_facto')  # Faktisch getrennt
add('60', _("Cohabitating"), 'cohabitating')


#~ '10', 'Célibataire', 'Ongehuwd', 'ledig'
#~ '13', 'Célibataire cohab.', NULL, 'ledig mit zus.',
#~ '18', 'Célibataire avec enf', NULL, 'ledig mit kind',
#~ '20', 'Marié', 'Gehuwd', 'verheiratet',
#~ '21', 'Séparé de fait', NULL, 'verheiratet alleine',
#~ '22', 'Séparé de fait cohab', NULL, 'verheiratet zus.',
#~ '30', 'Veuf(ve)', NULL, 'Witwe(r)',
#~ '33', 'Veuf(ve) cohab.', NULL, 'Witwe(r) zus.',
#~ '40', 'Divorcé', NULL, 'geschieden',
#~ '50', 'séparé(e) de corps', NULL, 'von Tisch & Bet get.',


class ResidenceTypes(dd.ChoiceList):

    """
    Types of registries for the Belgian residence.
    
    """
    verbose_name = _("Residence type")
    verbose_name_plural = _("Residence types")

add = ResidenceTypes.add_item
# Bevölkerungsregister registre de la population
add('1', _("Registry of citizens"))
# Fremdenregister        Registre des étrangers      vreemdelingenregister
add('2', _("Registry of foreigners"))
add('3', _("Waiting for registry"))    # Warteregister


class BeIdCardTypes(dd.ChoiceList):
    """A list of Belgian identity card types.

    Didn't yet find any official reference document.
    
    The eID applet returns a field `documentType` which contains a
    numeric code.  For example 1 is for "Belgian citizen", 6 for "Kids
    card",...
    
    The eID viewer, when saving a card as xml file, doesn't save these
    values nowhere, it saves a string equivalent (1 becomes
    "belgian_citizen", 6 becomes "kids_card", 17 becomes
    "foreigner_f", 16 becomes "foreigner_e_plus",...
    
    Sources:

    - [1] `kuleuven.be <https://securehomes.esat.kuleuven.be/~decockd/wiki/bin/view.cgi/EidForums/ForumEidCards0073>`__
    - [2] The `be.fedict.commons.eid.consumer.DocumentType <http://code.google.com/p/eid-applet/source/browse/trunk/eid-applet-service/src/main/java/be/fedict/eid/applet/service/DocumentType.java>`__ enum.

    - http://www.adde.be/joomdoc/guides/les-titres-de-sejours-en-belgique-guide-pratique-dec12-g-aussems-pdf/download


    Excerpts from [1]:
    
    - Johan: A document type of 7 is used for bootstrap cards -- What
      is a bootstrap card (maybe some kind of test card?)  Danny: A
      bootstrap card was an eID card that was used in the early start
      of the eID card introduction to bootstrap the computers at the
      administration. This type is no longer issued.
    
    - Johan: A document type of 8 is used for a
      "habilitation/machtigings" card -- Is this for refugees or
      asylum seekers? Danny: A habilitation/machtigings card was aimed
      at civil servants. This type is also no longer used.

    """

    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("eID card type")
    verbose_name_plural = _("eID card types")

add = BeIdCardTypes.add_item
add('1', _("Belgian citizen"), "belgian_citizen")
# ,de=u"Belgischer Staatsbürger",fr=u"Citoyen belge"),
add('6', _("Kids card (< 12 year)"), "kids_card")
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
