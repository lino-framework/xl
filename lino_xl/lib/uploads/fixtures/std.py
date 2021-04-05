# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _

from lino.modlib.uploads.choicelists import Shortcuts
from lino_xl.lib.cal.choicelists import Recurrencies

UPLOADTYPE_RESIDENCE_PERMIT = 2
UPLOADTYPE_WORK_PERMIT = 3
UPLOADTYPE_DRIVING_LICENSE = 4


def objects():
    UploadType = rt.models.uploads.UploadType

    kw = dict(
        warn_expiry_unit=Recurrencies.monthly,
        warn_expiry_value=2)
    kw.update(max_number=1, wanted=True)
    kw.update(dd.str2kw('name', _("Residence permit")))
    # 'name', de=u"Aufenthaltserlaubnis",
    # fr=u"Permis de séjour", en="Residence permit"))
    yield UploadType(id=UPLOADTYPE_RESIDENCE_PERMIT, **kw)

    kw.update(dd.str2kw('name', _("Work permit")))
        # 'name', de=u"Arbeitserlaubnis",
        # fr=u"Permis de travail", en="Work permit"))
    yield UploadType(id=UPLOADTYPE_WORK_PERMIT, **kw)

    kw.update(warn_expiry_value=1)

    kw.update(dd.str2kw('name', _("Driving licence")))
    yield UploadType(id=UPLOADTYPE_DRIVING_LICENSE, **kw)

    # kw.update(dd.str2kw('name', _("Identifying document")))
    # yield UploadType(shortcut=Shortcuts.id_document, **kw)

    for us in Shortcuts.get_list_items():
        kw.update(dd.str2kw('name', us.text))
        yield UploadType(shortcut=us, **kw)

    kw.update(max_number=-1, wanted=False)
    kw.update(warn_expiry_unit='')

    kw.update(dd.str2kw('name', _("Contract")))
    yield UploadType(**kw)

    kw.update(dd.str2kw('name', _("Medical certificate")))
    # de="Ärztliche Bescheinigung",
    # fr="Certificat médical",
    yield UploadType(**kw)

    kw.update(dd.str2kw('name', _("Handicap certificate")))
    # de="Behindertenausweis",
    # fr="Certificat de handicap",
    yield UploadType(**kw)

    kw.update(wanted=True)
    kw.update(dd.str2kw('name', _("Diploma")))
    yield UploadType(**kw)

    kw.update(wanted=False)
    kw.update(dd.str2kw('name', _("Identity card")))
    # fr=u"Carte d'identité", en="Identity card"))
    yield UploadType(**kw)
