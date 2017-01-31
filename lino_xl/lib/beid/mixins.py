# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
Actions and Choicelists used to read Belgian eID cards.

See unit tests in :mod:`lino_welfare.tests.test_beid`.

"""

import logging
logger = logging.getLogger(__name__)

import os
import yaml
import base64

from unipath import Path

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.exceptions import ValidationError

from lino.core.utils import get_field

from lino.core.diff import ChangeWatcher

from lino.utils.xmlgen.html import E
from lino.utils import AttrDict

from lino.api import dd, rt


from lino.utils import ssin
from lino.utils import join_words
from lino.utils import IncompleteDate
from lino_xl.lib.contacts.utils import street2kw
from lino.modlib.plausibility.choicelists import Checker
from .roles import BeIdUser

from .actions import BeIdReadCardAction, FindByBeIdAction
from .actions import get_image_parts, get_image_path

from .choicelists import BeIdCardTypes

MALE = Path(__file__).parent.child('luc.jpg')
FEMALE = Path(__file__).parent.child('ly.jpg')


class BeIdCardHolder(dd.Model):
    """Mixin for models which represent an eid card holder.
    Currently only Belgian eid cards are tested.
    Concrete subclasses must also inherit from :mod:`lino.mixins.Born`.

    .. attribute:: national_id

        The SSIN. It is a *nullable char field* declared *unique*. It
        is not validated directly because that would cause problems
        with legacy data where SSINs need manual control. See also
        :class:`BeIdCardHolderChecker`.

    .. attribute:: nationality

        The nationality. This is a pointer to
        :class:`countries.Country
        <lino_xl.lib.statbel.countries.models.Country>` which should
        contain also entries for refugee statuses.

        Note that the nationality is *not* being read from eID card
        because it is stored there as a language and gender specific
        plain text.

    .. attribute:: image

        Virtual field which displays the picture.

    """
    class Meta:
        abstract = True

    validate_national_id = False
    """Whether to validate the :attr:`national_id` immediately before
    saving a record.  If this is `False`, the :attr:`national_id`
    might contain invalid values which would then cause plausibility
    problems.

    """

    national_id = dd.NullCharField(
        max_length=200,
        unique=True,
        verbose_name=_("National ID")
        #~ blank=True,verbose_name=_("National ID")
        # ~ ,validators=[ssin.ssin_validator] # 20121108
    )

    birth_place = models.CharField(_("Birth place"),
                                   max_length=200,
                                   blank=True,
                                   #~ null=True
                                   )
    nationality = dd.ForeignKey('countries.Country',
                                blank=True, null=True,
                                related_name='by_nationality',
                                verbose_name=_("Nationality"))
    card_number = models.CharField(max_length=20,
                                   blank=True,  # null=True,
                                   verbose_name=_("eID card number"))
    card_valid_from = models.DateField(
        blank=True, null=True,
        verbose_name=_("ID card valid from"))
    card_valid_until = models.DateField(
        blank=True, null=True,
        verbose_name=_("until"))

    card_type = BeIdCardTypes.field(blank=True)

    card_issuer = models.CharField(max_length=50,
                                   blank=True,  # null=True,
                                   verbose_name=_("eID card issuer"))
    "The administration who issued this ID card."

    read_beid = BeIdReadCardAction()
    find_by_beid = FindByBeIdAction()

    noble_condition = models.CharField(
        max_length=50,
        blank=True,  # null=True,
        verbose_name=_("noble condition"),
        help_text=_("The eventual noble condition of this person."))

    beid_readonly_fields = set(
        'noble_condition card_valid_from card_valid_until \
        card_issuer card_number card_type'.split())

    def disabled_fields(self, ar):
        rv = super(BeIdCardHolder, self).disabled_fields(ar)
        if not ar.get_user().profile.has_required_roles([dd.SiteStaff]):
            rv |= self.beid_readonly_fields
        #~ logger.info("20130808 beid %s", rv)
        return rv

    def has_valid_card_data(self, today=None):
        if not self.card_number:
            return False
        if self.card_valid_until < (today or dd.today()):
            return False
        return True

    def full_clean(self):
        if self.validate_national_id and self.national_id:
            self.national_id = ssin.parse_ssin(self.national_id)
        super(BeIdCardHolder, self).full_clean()
    
    @dd.displayfield(_("eID card"), default='<br/><br/><br/><br/>')
    def eid_info(self, ar):
        "Display some information about the eID card."
        attrs = dict(class_="lino-info")
        if ar is None:
            return E.div(**attrs)
        must_read = False
        elems = []
        if self.card_number:
            elems += ["%s %s (%s)" %
                      (ugettext("Card no."), self.card_number, self.card_type)]
            if self.card_issuer:
                elems.append(", %s %s" %
                             (ugettext("issued by"), self.card_issuer))
                #~ card_issuer = _("issued by"),
            if self.card_valid_until is not None:
                valid = ", %s %s %s %s" % (
                    ugettext("valid from"), dd.dtos(self.card_valid_from),
                    ugettext("until"), dd.dtos(self.card_valid_until))
                if self.card_valid_until < dd.today():
                    must_read = True
                    elems.append(E.b(valid))
                    elems.append(E.br())
                else:
                    elems.append(valid)

            else:
                must_read = True
        else:
            must_read = True
        if must_read:
            msg = _("Must read eID card!")
            if dd.plugins.beid:
                elems.append(ar.instance_action_button(
                    self.read_beid, msg, icon_name=None))
            else:
                elems.append(msg)
            # same red as in lino.css for .x-grid3-row-red td
            # ~ attrs.update(style="background-color:#FA7F7F; padding:3pt;")
            attrs.update(class_="lino-info-red")
        return E.div(*elems, **attrs)

    def get_beid_diffs(obj, attrs):
        """Return two lists, one with the objects to save, and another with
        text lines to build a confirmation message explaining which
        changes are going to be applied after confirmation.

        The default implemantion is for the simple case where the
        holder is also a contacts.AddressLocation and the address is
        within the same database row.

        """
        raise Exception("not tested")
        diffs = []
        objects = []
        # model = holder_model()
        model = obj.__class__  # the holder
        for fldname, new in attrs.items():
            fld = get_field(model, fldname)
            old = getattr(obj, fldname)
            if old != new:
                diffs.append(
                    "%s : %s -> %s" % (
                        unicode(fld.verbose_name), dd.obj2str(old),
                        dd.obj2str(new)))
                setattr(obj, fld.name, new)
        return objects, diffs

    @dd.htmlbox()
    def image(self, ar):
        url = self.get_image_url(ar)
        return E.a(E.img(src=url, width="100%"), href=url, target="_blank")
        # s = '<img src="%s" width="100%%"/>' % url
        # s = '<a href="%s" target="_blank">%s</a>' % (url, s)
        # return s

    def get_image_url(self, ar):
        if self.card_number:
            parts = get_image_parts(self.card_number)
            return settings.SITE.build_media_url(*parts)
        return settings.SITE.build_static_url("contacts.Person.jpg")

    def get_image_path(self):
        return get_image_path(self.card_number)

    def make_demo_picture(self):
        """Create a demo picture for this card holder. """
        if not self.card_number:
            raise Exception("20150730")
        src = self.mf(MALE, FEMALE)
        dst = self.get_image_path()
        # dst = settings.SITE.cache_dir.child(
        #     'media', 'beid', self.card_number + '.jpg')
        if dst.needs_update([src]):
            logger.info("Create demo picture %s", dst)
            settings.SITE.makedirs_if_missing(dst.parent)
            src.copy(dst)
        else:
            logger.info("Demo picture %s is up-to-date", dst)


class BeIdCardHolderChecker(Checker):
    """Invalid NISSes are not refused à priori using a ValidationError
    (see :attr:`BeIdCardHolder.national_id`), but this checker reports
    them.

    Belgian NISSes are stored including the formatting characters (see
    :mod:`lino.utils.ssin`) in order to guarantee uniqueness.

    """
    model = BeIdCardHolder
    verbose_name = _("Check for invalid SSINs")

    def get_plausibility_problems(self, obj, fix=False):
        if obj.national_id:
            try:
                expected = ssin.parse_ssin(obj.national_id)
            except ValidationError as e:
                yield (False, _("Cannot fix invalid SSIN ({0})").format(e))
            else:
                got = obj.national_id
                if got != expected:
                    msg = _("Malformed SSIN '{got}' must be '{expected}'.")
                    params = dict(expected=expected, got=got, obj=obj)
                    yield (True, msg.format(**params))
                    if fix:
                        obj.national_id = expected
                        try:
                            obj.full_clean()
                        except ValidationError as e:
                            msg = _("Failed to fix malformed "
                                    "SSIN '{got}' of '{obj}'.")
                            msg = msg.format(**params)
                            raise Warning(msg)
                        obj.save()

BeIdCardHolderChecker.activate()


