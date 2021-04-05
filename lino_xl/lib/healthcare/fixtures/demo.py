# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str

# from lino.utils.instantiator import Instantiator
from lino.api import rt, dd, _


Company = rt.models.contacts.Company
Plan = rt.models.healthcare.Plan

def objects():
    # source: https://www.riziv.fgov.be/fr/professionnels/autres/mutualites/Pages/contactez-mutualites.aspx
    bxl = rt.models.countries.Place.objects.get(**dd.babel_values('name', de="Brüssel", en="Brussels"))
    kw = dict(country_id="BE", city=bxl)

    def provider(ref, name, **kwargs):
        prov = Company(name=name, **kwargs)
        yield prov
        yield Plan(provider=prov, ref=ref)

    yield provider(_("Christian HIS"), "Alliance nationale des mutualités chrétiennes", street="Haachtsesteenweg 579", street_box="postbus 40", zip_code="1031")
    yield provider(_("Neutral HIS"), "Union nationale des mutualités neutres", street="Chaussée de Charleroi", street_no="145", zip_code="1060")
    yield provider(_("Socialist HIS"), "Union nationale des mutualités socialistes", street="Rue Saint-Jean", street_no="32-38", zip_code="1000")
    yield provider(_("Liberal HIS"), "Union nationale des Mutualités Libérales", street="Rue de Livourne", street_no="25", zip_code="1050")
    yield provider(_("Libre HIS"), "Union nationale des mutualités libres", street="Lenniksebaan", street_no="788A", zip_code="1070")

