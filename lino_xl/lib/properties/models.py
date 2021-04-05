# -*- coding: UTF-8 -*-
# Copyright 2008-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from builtins import str

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from lino.core.roles import SiteStaff
from lino.api import dd, rt
from lino import mixins

from lino.core.kernel import get_choicelist, choicelist_choices

MULTIPLE_VALUES_SEP = ','

from .choicelists import DoYouLike, HowWell


class PropType(mixins.BabelNamed):
    class Meta:
        verbose_name = _("Property Type")
        verbose_name_plural = _("Property Types")

    #~ name = dd.BabelCharField(max_length=200,verbose_name=_("Designation"))

    choicelist = models.CharField(
        max_length=50, blank=True,
        verbose_name=_("Choices List"))

    default_value = models.CharField(
        _("default value"),
        max_length=settings.SITE.propvalue_max_length,
        blank=True)

    limit_to_choices = models.BooleanField(
        _("Limit to choices"), default=False)
    """
    not yet supported
    """

    multiple_choices = models.BooleanField(
        _("Multiple choices"), default=False)
    """
    not yet supported
    """

    @dd.chooser()
    def choicelist_choices(cls):
        # Must be a chooser (not simply a default value on the field) because the
        # list is not known at startup when models are being imported.
        return choicelist_choices()

    @dd.chooser()
    def default_value_choices(cls, choicelist):
        if choicelist:
            return get_choicelist(choicelist).get_choices()
        return []

    def get_default_value_display(self, value):
        return self.get_text_for_value(value)

    def get_text_for_value(self, value):
        if not value:
            return ''
        if self.choicelist:
            cl = get_choicelist(self.choicelist)
            return cl.get_text_for_value(value)
        l = []
        for v in value.split(MULTIPLE_VALUES_SEP):
            try:
                pc = PropChoice.objects.get(value=v, type=self)
                v = dd.babelattr(pc, 'text')
            except PropChoice.DoesNotExist:
                pass
            l.append(v)
        return ','.join(l)

    #~ def __unicode__(self):
        #~ return dd.babelattr(self,'name')

    def choices_for(self, property):
        if self.choicelist:
            return get_choicelist(self.choicelist).get_choices()
        return [(pc.value, pc.text) for pc in
                PropChoice.objects.filter(type=self).order_by('value')]



class PropChoice(dd.Model):
    class Meta:
        verbose_name = _("Property Choice")
        verbose_name_plural = _("Property Choices")
        unique_together = ['type', 'value']

    type = dd.ForeignKey(
        PropType, verbose_name=_("Property Type"))
    value = models.CharField(
        max_length=settings.SITE.propvalue_max_length,
        verbose_name=_("Value"))
    text = dd.BabelCharField(
        max_length=200, verbose_name=_("Designation"), blank=True)

    def save(self, *args, **kw):
        if not self.text:
            self.text = self.value
        r = super(PropChoice, self).save(*args, **kw)
        return r

    def __str__(self):
        return dd.babelattr(self, 'text')


class PropGroup(mixins.BabelNamed):
    class Meta:
        verbose_name = _("Property Group")
        verbose_name_plural = _("Property Groups")


class Property(mixins.BabelNamed):

    class Meta:
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")

    group = dd.ForeignKey(PropGroup)
    type = dd.ForeignKey(PropType, verbose_name=_("Property Type"))



class PropertyOccurence(dd.Model):


    class Meta:
        abstract = True

    group = dd.ForeignKey(PropGroup)
    property = dd.ForeignKey('properties.Property')
    value = models.CharField(
        _("Value"),
        max_length=settings.SITE.propvalue_max_length,
        blank=True)

    @dd.chooser()
    def value_choices(cls, property):
        if property is None:
            return []
        return property.type.choices_for(property)

    @dd.chooser()
    def property_choices(cls, group):
        #~ print 20120212, group
        if group is None:
            return []
        return Property.objects.filter(group=group).order_by('name')

    def get_value_display(self, value):
        if self.property_id is None:
            return value
        return self.property.type.get_text_for_value(value)

    def full_clean(self):
        if self.property_id is not None:
            self.group = self.property.group
        super(PropertyOccurence, self).full_clean()

    def __str__(self):
        if self.property_id is None:
            return u"Undefined %s" % self.group
        # We must call str() because get_text_for_value might return a
        # lazyly translatable string:
        return str(self.property.type.get_text_for_value(self.value))
        # try:
        #     return str(self.property.type.get_text_for_value(self.value))
        # except UnicodeError:
        #     value = self.property.type.get_text_for_value(self.value)
        #     raise Exception("Failed get_text_for_value(%s, %r)" % (
        #         self.property.type.choicelist, value))

    #~ def __unicode__(self):
        #~ if self.property_id is None:
            #~ return u"Undefined %s" % self.group
        #~ return u'%s.%s=%s' % (
            #~ self.group,self.property,
            #~ self.property.type.get_text_for_value(self.value))


class PropGroups(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = PropGroup
    detail_layout = """
    id name
    PropsByGroup
    """


class PropTypes(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = PropType
    detail_layout = """
    id name choicelist default_value
    ChoicesByType
    PropsByType
    """


class Properties(dd.Table):
    required_roles = dd.login_required(dd.SiteStaff)
    model = Property
    order_by = ['name']
    #~ column_names = "id name"


class PropsByGroup(Properties):
    master_key = 'group'


class PropsByType(Properties):
    master_key = 'type'


class PropChoices(dd.Table):
    model = PropChoice


class ChoicesByType(PropChoices):

    "Lists all PropChoices for a given PropType."
    master_key = 'type'
    order_by = ['value']
    column_names = 'value text *'
