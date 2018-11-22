# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str
from builtins import object

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from lino.api import dd, rt
from lino.utils.addressable import Addressable

from .choicelists import CountryDrivers, PlaceTypes
from .utils import get_address_formatter


class CountryCity(dd.Model):

    class Meta(object):
        abstract = True

    country = dd.ForeignKey(
        "countries.Country", blank=True, null=True)
    city = dd.ForeignKey(
        'countries.Place',
        verbose_name=_('Locality'),
        blank=True, null=True)
    zip_code = models.CharField(_("Zip code"), max_length=10, blank=True)

    active_fields = 'city zip_code'
    # active fields cannot be used in insert_layout

    @dd.chooser()
    def city_choices(cls, country):
        return rt.models.countries.Place.get_cities(country)

    @dd.chooser()
    def country_choices(cls):
        return rt.models.countries.Country.get_actual_countries()

    def create_city_choice(self, text):
        """
        Called when an unknown city name was given.
        Try to auto-create it.
        """
        if self.country is not None:
            return rt.models.countries.Place.lookup_or_create(
                'name', text, country=self.country)

        raise ValidationError(
            "Cannot auto-create city %r if country is empty", text)

    def country_changed(self, ar):
        """
        If user changes the `country`, then the `city` gets lost.
        """
        if self.city is not None and self.country != self.city.country:
            self.city = None

    def zip_code_changed(self, ar):
        if self.country and self.zip_code:
            qs = rt.models.countries.Place.objects.filter(
                country=self.country, zip_code=self.zip_code)
            if qs.count() > 0:
                self.city = qs[0]

    def full_clean(self, *args, **kw):
        """Fills my :attr:`zip_code` from my :attr:`city` if my `zip_code` is
        not empty and differs from that of the city.

        """
        city = self.city
        if city is None:
            self.zip_code_changed(None)
        else:
            if city.country is not None and self.country != city.country:
                self.country = city.country
            if city.zip_code:
                self.zip_code = city.zip_code
        super(CountryCity, self).full_clean(*args, **kw)


class CountryRegionCity(CountryCity):
    region = dd.ForeignKey(
        'countries.Place',
        blank=True, null=True,
        verbose_name=dd.plugins.countries.region_label,
        related_name="%(app_label)s_%(class)s_set_by_region")
        #~ related_name='regions')

    class Meta(object):
        abstract = True

    @dd.chooser()
    def region_choices(cls, country):
        Place = rt.models.countries.Place
        if country is not None:
            cd = getattr(CountryDrivers, country.isocode, None)
            if cd:
                flt = models.Q(type__in=cd.region_types)
            else:
                flt = models.Q(type__lt=PlaceTypes.get_by_value('50'))
            #~ flt = flt | models.Q(type=PlaceTypes.blank_item)
            flt = flt & models.Q(country=country)
            return Place.objects.filter(flt).order_by('name')
        else:
            flt = models.Q(type__lt=PlaceTypes.get_by_value('50'))
            return Place.objects.filter(flt).order_by('name')

    def create_city_choice(self, text):
        # if a Place is created by super, then we add our region
        obj = super(CountryRegionCity, self).create_city_choice(text)
        obj.region = self.region
        return obj

    @dd.chooser()
    def city_choices(cls, country, region):
        qs = super(CountryRegionCity, cls).city_choices(country)

        if region is not None:
            parent_list = [p.pk for p in region.get_parents()] + [None]
            #~ print 20120822, region,region.get_parents(), parent_list
            qs = qs.filter(parent__id__in=parent_list)
            #~ print flt

        return qs

            #~ return country.place_set.filter(flt).order_by('name')
        #~ return cls.city.field.rel.model.objects.order_by('name')


class AddressLocation(CountryRegionCity, Addressable):
    class Meta(object):
        abstract = True

    addr1 = models.CharField(
        _("Address line before street"),
        max_length=200, blank=True)
    street_prefix = models.CharField(
        _("Street prefix"), max_length=200, blank=True)
    street = models.CharField(
        _("Street"), max_length=200, blank=True)
    street_no = models.CharField(
        _("No."), max_length=10, blank=True)
    street_box = models.CharField(
        _("Box"), max_length=10, blank=True)
    addr2 = models.CharField(
        _("Address line after street"),
        max_length=200, blank=True)

    def on_create(self, ar):
        sc = settings.SITE.site_config.site_company
        if sc and sc.country:
            self.country = sc.country
        super(AddressLocation, self).on_create(ar)

    def get_primary_address(self):
        """Return the primary address of this partner.

        Return value must be either None or an instance of
        :class:`AddressLocation`.

        """
        return self
        
    def address_location_lines(self):
        #~ lines = []
        #~ lines = [self.name]
        af = get_address_formatter(self.country)

        if self.addr1:
            yield self.addr1
        for ln in af.get_street_lines(self):
            yield ln
        if self.addr2:
            yield self.addr2

        for ln in af.get_city_lines(self):
            yield ln

        if self.country is not None:
            kodu = dd.plugins.countries.get_my_country()
            if kodu is None or self.country != kodu:
                # (if self.country != sender's country)
                yield str(self.country)

        #~ logger.debug('%s : as_address() -> %r',self,lines)

    def address_location(self, linesep="\n"):
        return linesep.join(self.address_location_lines())

    @dd.displayfield(_("Address"))
    def address_column(self, ar):
        return self.address_location(', ')


