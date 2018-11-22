# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""
See :mod:`ml.cv`.
"""
from __future__ import unicode_literals
from builtins import str

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from etgen.html import E, join_elems

from lino.mixins.periods import DateRange

class BiographyOwner(dd.Model):
    
    class Meta:
        abstract = True

    _cef_levels = None
    _mother_tongues = None
    
    def load_language_knowledge(self):
        if self._mother_tongues is not None:
            return
        LanguageKnowledge = rt.models.cv.LanguageKnowledge
        self._cef_levels = dict()
        self._mother_tongues = []
        for lk in LanguageKnowledge.objects.filter(
                person=self).order_by('id'):
            if lk.native:
                self._mother_tongues.append(lk.language)
            # if lk.language.iso2 in ("de", "fr", "en"):
            if lk.cef_level is not None:
                self._cef_levels[lk.language.iso2] = lk.cef_level.value
        
    @dd.htmlbox(_("Language knowledge"))
    def language_knowledge(self, ar):
        return self.get_language_knowledge()
    
    def get_language_knowledge(self, *buttons):
        self.load_language_knowledge()
        lst = []
        for lng in settings.SITE.languages:
            cl = self._cef_levels.get(lng.django_code, "---")
            lst.append("{}: {}".format(lng.name, cl))
            # if cl is None:
            #     lst.append("{}: {}".format(lng.name, ))
            # else:
            #     lst.append("{}: {}".format(lng.name, cl))
        if len(self._mother_tongues):
            lst.append("{}: {}".format(
                _("Mother tongues"), self.mother_tongues))
        lst += buttons
        lst = join_elems(lst, E.br)
        return E.p(*lst)
                
    
    @dd.displayfield(_("Mother tongues"))
    def mother_tongues(self, ar):
        self.load_language_knowledge()
        return ' '.join([str(lng) for lng in self._mother_tongues])

    # @dd.displayfield(_("CEF level (de)"))
    @dd.displayfield()
    def cef_level_de(self, ar):
        self.load_language_knowledge()
        return self._cef_levels.get('de')

    # @dd.displayfield(_("CEF level (fr)"))
    @dd.displayfield()
    def cef_level_fr(self, ar):
        self.load_language_knowledge()
        return self._cef_levels.get('fr')

    # @dd.displayfield(_("CEF level (en)"))
    @dd.displayfield()
    def cef_level_en(self, ar):
        self.load_language_knowledge()
        return self._cef_levels.get('en')


class EducationEntryStates(dd.ChoiceList):
    """The possible states of an **education entry**.

    """
    verbose_name = _("State")

add = EducationEntryStates.add_item
add('0', _("Success"), 'success')
add('1', _("Failure"), 'failure')
add('2', _("Ongoing"), 'ongoing')


class HowWell(dd.ChoiceList):

    """A list of possible answers to questions of type "How well ...?":
    "not at all", "a bit", "moderate", "quite well" and "very well"
    
    which are stored in the database as '0' to '4',
    and whose `__str__()` returns their translated text.

    """
    verbose_name = _("How well?")

add = HowWell.add_item
add('0', _("not at all"))
add('1', _("a bit"))
add('2', _("moderate"), "default")
add('3', _("quite well"))
add('4', _("very well"))


class CefLevel(dd.ChoiceList):

    """
    Levels of the Common European Framework (CEF).
    
    | http://www.coe.int/t/dg4/linguistic/CADRE_EN.asp
    | http://www.coe.int/t/dg4/linguistic/Source/ManualRevision-proofread-FINAL_en.pdf
    | http://www.telc.net/en/what-telc-offers/cef-levels/a2/
    
    """
    verbose_name = _("CEF level")
    verbose_name_plural = _("CEF levels")
    show_values = True

    #~ @classmethod
    #~ def display_text(cls,bc):
        #~ def fn(bc):
            #~ return u"%s (%s)" % (bc.value,unicode(bc))
        #~ return lazy(fn,unicode)(bc)

add = CefLevel.add_item
add('A0', _("basic language skills"))
add('A1', _("basic language skills"))
add('A1+', _("basic language skills"))
add('A2', _("basic language skills"))
add('A2+', _("basic language skills"))
add('B1', _("independent use of language"))
add('B2', _("independent use of language"))
add('B2+', _("independent use of language"))
add('C1', _("proficient use of language"))
add('C2', _("proficient use of language"))
add('C2+', _("proficient use of language"))


class SectorFunction(dd.Model):

    """
    Abstract base for models that refer to a
    :class:`Sector` and a :class:`Function`.
    """
    class Meta:
        abstract = True

    sector = dd.ForeignKey("cv.Sector", blank=True, null=True)
    function = dd.ForeignKey("cv.Function", blank=True, null=True)

    @dd.chooser()
    def function_choices(cls, sector):
        if sector is None:
            return rt.models.cv.Function.objects.all()
        return sector.function_set.all()


class PersonHistoryEntry(DateRange):
    "Base class for Study, Experience"
    class Meta:
        abstract = True

    person = dd.ForeignKey(dd.plugins.cv.person_model)
    duration_text = models.CharField(
        _("Duration"), max_length=200, blank=True)



class HistoryByPerson(dd.Table):
    """Abstract base class for :class:`StudiesByPerson` and
    :class:`ExperiencesByPerson`

    """
    master_key = 'person'
    order_by = ["start_date"]
    auto_fit_column_widths = True

    @classmethod
    def create_instance(self, req, **kw):
        obj = super(HistoryByPerson, self).create_instance(req, **kw)
        if obj.person_id is not None:
            previous_exps = self.model.objects.filter(
                person=obj.person).order_by('start_date')
            if previous_exps.count() > 0:
                exp = previous_exps[previous_exps.count() - 1]
                if exp.end_date:
                    obj.start_date = exp.end_date
                else:
                    obj.start_date = exp.start_date
        return obj


