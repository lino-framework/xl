# -*- coding: UTF-8 -*-
# Copyright 2008-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str
from builtins import object

import logging ; logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings

from lino.api import dd
from lino import mixins
from django.utils.translation import ugettext_lazy as _
from lino.modlib.checkdata.choicelists import Checker
from lino_xl.lib.contacts.roles import ContactsUser, ContactsStaff

from .choicelists import PlaceTypes, CountryDrivers


FREQUENT_COUNTRIES = ['BE', 'NL', 'DE', 'FR', 'LU']
"""A list of frequent countries used by some demo fixtures."""


class Country(mixins.BabelNamed):

    class Meta(object):
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        abstract = dd.is_abstract_model(__name__, 'Country')
        ordering = ['isocode']

    isocode = models.CharField(
        max_length=4, primary_key=True,verbose_name=_("ISO code"))

    short_code = models.CharField(
        max_length=4, blank=True,
        verbose_name=_("Short code"))

    iso3 = models.CharField(
        max_length=3, blank=True,
        verbose_name=_("ISO-3 code"))

    def allowed_city_types(self):
        cd = getattr(CountryDrivers, self.isocode, None)
        if cd is not None:
            return cd.region_types + cd.city_types
        return PlaceTypes.get_list_items()

    @classmethod
    def get_actual_countries(cls):
        return cls.objects.all()

Country.set_widget_options('short_code', width=10)
Country.set_widget_options('isocode', width=10)


class Countries(dd.Table):
    """The table of all countries."""

    #~ label = _("Countries")
    model = 'countries.Country'
    required_roles = dd.login_required(ContactsStaff)
    order_by = ["name", "isocode"]
    column_names = "name isocode *"
    detail_layout = """
    isocode name short_code
    countries.PlacesByCountry
    """
    insert_layout = """
    isocode short_code
    name
    """

from lino.mixins import Hierarchical


# @dd.python_2_unicode_compatible
class Place(Hierarchical, mixins.BabelNamed):
    class Meta(object):
        verbose_name = _("Place")
        verbose_name_plural = _("Places")
        abstract = dd.is_abstract_model(__name__, 'Place')

        if not settings.SITE.allow_duplicate_cities:
            unique_together = (
                'country', 'parent', 'name', 'type', 'zip_code')

    country = dd.ForeignKey('countries.Country')
    zip_code = models.CharField(max_length=8, blank=True)
    type = PlaceTypes.field(blank=True)
    show_type = models.BooleanField(_("Show type"), default=False)
    
    @dd.chooser()
    def type_choices(cls, country):
        if country is not None:
            allowed = country.allowed_city_types()
            #return [(i, t) for i, t in PlaceTypes.choices if i in allowed]
            return allowed
        return PlaceTypes.choices

    def get_choices_text(self, request, actor, field):
        names = [self.name]
        for lng in settings.SITE.BABEL_LANGS:
            n = getattr(self, 'name' + lng.suffix)
            if n and n not in names:
                names.append(n)
                #~ s += ' / ' + n
        if len(names) == 1:
            s = names[0]
        else:
            s = ' / '.join(names)
            # s = "%s (%s)" % (names[0], ', '.join(names[1:]))
        if self.show_type:
            s += " (%s)" % str(self.type)
        if self.zip_code:
            s = self.zip_code + " " + s
        return s

    @classmethod
    def get_cities(cls, country):
        if country is None:
            cd = None
            flt = models.Q()
        else:
            cd = getattr(CountryDrivers, country.isocode, None)
            flt = models.Q(country=country)

        #~ types = [PlaceTypes.blank_item] 20120829
        types = [None]
        if cd:
            types += cd.city_types
            #~ flt = flt & models.Q(type__in=cd.city_types)
        else:
            types += [v for v in list(PlaceTypes.items()) if v.value >= '50']
            #~ flt = flt & models.Q(type__gte=PlaceTypes.get_by_value('50'))
        flt = flt & models.Q(type__in=types)
        #~ flt = flt | models.Q(type=PlaceTypes.blank_item)
        return cls.objects.filter(flt).order_by('name')

        #~ if country is not None:
            #~ cd = getattr(CountryDrivers,country.isocode,None)
            #~ if cd:
                #~ return Place.objects.filter(
                    #~ country=country,
                    #~ type__in=cd.city_types).order_by('name')
            #~ return country.place_set.order_by('name')
        #~ return cls.city.field.rel.model.objects.order_by('name')

dd.update_field(Place, 'parent', verbose_name=_("Part of"))


class Places(dd.Table):

    model = 'countries.Place'
    required_roles = dd.login_required(ContactsStaff)
    order_by = "country name".split()
    column_names = "country name type zip_code parent *"
    detail_layout = """
    name country
    type parent zip_code id
    PlacesByPlace
    """


class PlacesByPlace(Places):
    label = _("Subdivisions")
    master_key = 'parent'
    column_names = "detail_link type zip_code *"


class PlacesByCountry(Places):
    master_key = 'country'
    column_names = "name type zip_code *"
    required_roles = dd.login_required()
    details_of_master_template = _("%(details)s in %(master)s")


class PlaceChecker(Checker):
    model = 'countries.Place'
    verbose_name = _("Check data of geographical places.")

    def get_checkdata_problems(self, obj, fix=False):
        if obj.name.isdigit():
            yield (False, _("Name contains only digits."))

PlaceChecker.activate()
