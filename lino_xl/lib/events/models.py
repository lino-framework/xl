# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Luc Saffre
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
The :xfile:`models.py` module of :mod:`lino_xl.lib.events`.
"""

from __future__ import unicode_literals
from builtins import str

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

from etgen.html import E
from lino.api import dd
from lino import mixins
from lino.core.constants import _handle_attr_name


def sepjoin(items, sep=', '):
    rv = []
    for i in items:
        if len(rv):
            rv.append(sep)
        rv.append(str(i))
    return rv


class Place(mixins.BabelNamed):
    city = dd.ForeignKey(
        'countries.Place',
        related_name='events_place_set',
        blank=True, null=True)


class Places(dd.Table):
    model = Place


class Feature(mixins.BabelNamed):
    pass


class Features(dd.Table):
    model = Feature


class Type(mixins.BabelNamed):
    
    events_column_names = models.CharField(
        max_length=100,
        default="when:30 what:40 where:30")

    def EventsByType(self, year=None, **kw):
        kw.update(master_instance=self)

        if year is None:
            year = settings.SITE.today().year
        kw.update(filter=models.Q(date__year=year))

        return VariableEventsByType.request(**kw)


class Types(dd.Table):
    model = Type
    
    detail_layout = """
    name id
    events.EventsByType
    """
    


class Event(mixins.BabelNamed):
    date = models.DateField(_("Date"))
    place = dd.ForeignKey(Place, blank=True, null=True)
    type = dd.ForeignKey(Type)
    features = models.ManyToManyField(Feature)
    #~ cities = models.ManyToManyField('countries.Place')
    #~ description = dd.BabelTextField(format='plain',blank=True)
    url = models.URLField(blank=True)



class Stage(mixins.Sequenced):
    event = dd.ForeignKey('events.Event', related_name="stages")
    city = dd.ForeignKey('countries.Place', related_name="stages")

    def __str__(self):
        return str(self.city)

    def get_siblings(self):
        return self.event.stages.all()

dd.update_field(Event, 'name', blank=True)


class StagesByEvent(dd.Table):
    model = Stage  # Event.cities.through
    master_key = 'event'


class FeaturesByEvent(dd.Table):
    model = Event.features.through
    master_key = 'event'


class Events(dd.Table):
    model = Event
    order_by = ['date']
    column_names = "date place type"
    detail_layout = """
    type date place
    StagesByEvent FeaturesByEvent
    """

    @dd.displayfield(format_lazy(u"{}{}",_("When"), "?"))
    def when(self, obj, ar):
        #~ rv = dbutils.dtosl(obj.date)
        rv = dd.fdf(obj.date)
        if obj.url:
            # replaces spaces by newline to avoid large column
            rv = '\n'.join(rv.split())
            rv = E.a(rv, href=obj.url)
        return rv

    @dd.displayfield(format_lazy(u"{}{}",_("Where"), "?"))
    def where(self, obj, ar):
        if obj.place is not None:
            return E.p(str(obj.place), ' ', E.b(str(obj.place.city)))
        # remember: "von Ans nach Eupen und nicht andersrum"
        return E.p(*sepjoin(obj.stages.order_by('seqno'), ' -- '))

    @dd.displayfield(format_lazy(u"{}{}",_("What"), "?"))
    def what(self, obj, ar):
        chunks = []
        if obj.name:
            chunks += [E.b(str(obj)), E.br()]
        chunks += sepjoin(obj.features.all())
        #~ if obj.url:
            #~ chunks += [E.br(),E.a(_("More"),href=obj.url)]
        return E.p(*chunks)


class EventsByType(Events):
    master_key = 'type'

    @classmethod
    def get_column_names(self, ar):
        if ar is None:
            return 'when:30 what:40 where:30'
        return ar.master_instance.events_column_names

class VariableEventsByType(EventsByType):
    
    @classmethod
    def get_title_base(self, ar):
        if ar is not None:
            return str(ar.master_instance)
        
    @classmethod
    def get_handle_name(self, ar):
        hname = _handle_attr_name
        hname += ar.master_instance.events_column_names.replace(" ", "_")
        return hname


