# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Database models for this plugin.

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from lino.api import dd, rt

from lino import mixins

from lino.modlib.users.mixins import UserAuthored
from lino.modlib.notify.mixins import ChangeObservable
from lino.modlib.plausibility.choicelists import Checker

from .mixins import ClientContactBase
from .choicelists import ClientEvents, ClientStates


try:
    client_model = dd.plugins.coachings.client_model
except AttributeError:  # for Sphinx autodoc
    client_model = None
    
INTEG_LABEL = _("Integration")
GSS_LABEL = _("GSS")  # General Social Service


class CoachingType(mixins.BabelNamed):

    """.. attribute:: does_integ

        Whether coachings of this type are to be considered as
        integration work. This is used when generating calendar events
        for evaluation meetings (see
        :meth:`lino_welfare.modlib.isip.mixins.ContractBase.setup_auto_event`)

    """
    class Meta:
        app_label = 'coachings'
        verbose_name = _("Coaching type")
        verbose_name_plural = _('Coaching types')

    does_integ = models.BooleanField(
        INTEG_LABEL, default=True,
        help_text=_("Whether this coaching type does integration."))

    does_gss = models.BooleanField(
        GSS_LABEL, default=True,
        help_text=_("Whether this coaching type does general social work."))

    eval_guestrole = dd.ForeignKey(
        'cal.GuestRole',
        verbose_name=_("Role in evaluations"),
        help_text=_("Role when participating in evaluation meetings."),
        blank=True, null=True)


class CoachingEnding(mixins.BabelNamed, mixins.Sequenced):

    class Meta:
        app_label = 'coachings'
        verbose_name = _("Reason of termination")
        verbose_name_plural = _('Coaching termination reasons')

    #~ name = models.CharField(_("designation"),max_length=200)
    type = dd.ForeignKey(
        CoachingType,
        blank=True, null=True,
        help_text=_("If not empty, allow this ending only on "
                    "coachings of specified type."))


@dd.python_2_unicode_compatible
class Coaching(UserAuthored, mixins.DatePeriod, dd.ImportedFields, ChangeObservable):

    """A Coaching ("Begleitung" in German and "intervention" in French) is
    when a given client is being coached by a given user during a
    given period.  

    For example in :ref:`welfare` that used is a social assistant.

    """

    class Meta:
        app_label = 'coachings'
        verbose_name = _("Coaching")
        verbose_name_plural = _("Coachings")

    # user = models.ForeignKey(
    #     settings.SITE.user_model,
    #     verbose_name=_("Coach"),
    #     related_name="%(app_label)s_%(class)s_set_by_user",
    # )

    allow_cascaded_delete = ['client']
    workflow_state_field = 'state'

    client = dd.ForeignKey(
        client_model, related_name="coachings_by_client")
    type = dd.ForeignKey('coachings.CoachingType', blank=True, null=True)
    primary = models.BooleanField(
        _("Primary"),
        default=False,
        help_text=_("""There's at most one primary coach per client. \
        Enabling this field will automatically make the other \
        coachings non-primary."""))

    ending = models.ForeignKey(
        'coachings.CoachingEnding',
        related_name="%(app_label)s_%(class)s_set",
        blank=True, null=True)

    @classmethod
    def on_analyze(cls, site):
        super(Coaching, cls).on_analyze(site)
        cls.declare_imported_fields('''client user primary end_date''')

    @dd.chooser()
    def ending_choices(cls, type):
        qs = CoachingEnding.objects.filter(
            Q(type__isnull=True) | Q(type=type))
        return qs.order_by("seqno")

    def disabled_fields(self, ar):
        rv = super(Coaching, self).disabled_fields(ar)
        if settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return self._imported_fields
            return set(['primary'])
        return rv

    def on_create(self, ar):
        """
        Default value for the `user` field is the requesting user.
        """
        if self.user_id is None:
            u = ar.get_user()
            if u is not None:
                self.user = u
        super(Coaching, self).on_create(ar)

    def disable_delete(self, ar=None):
        if ar is not None and settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return _("Cannot delete companies and persons imported from TIM")
        return super(Coaching, self).disable_delete(ar)

    def before_ui_save(self, ar, **kw):
        #~ logger.info("20121011 before_ui_save %s",self)
        super(Coaching, self).before_ui_save(ar, **kw)
        if not self.type:
            self.type = ar.get_user().coaching_type
        if not self.start_date:
            self.start_date = settings.SITE.today()
        if self.ending and not self.end_date:
            self.end_date = settings.SITE.today()

    #~ def update_system_note(self,note):
        #~ note.project = self.client

    def __str__(self):
        #~ return _("Coaching of %(client)s by %(user)s") % dict(client=self.client,user=self.user)
        #~ return self.user.username+' / '+self.client.first_name+' '+self.client.last_name[0]
        cl = self.client
        if self.user_id is None:
            return "{} {}".format(
                self.__class__._meta.verbose_name, cl)
        if cl.first_name:
            return self.user.username + ' / ' + cl.last_name + ' ' + cl.first_name[0]
        return self.user.username + ' / ' + cl.last_name

    def after_ui_save(self, ar, cw):
        super(Coaching, self).after_ui_save(ar, cw)
        if self.primary:
            for c in self.client.coachings_by_client.exclude(id=self.id):
                if c.primary:
                    c.primary = False
                    c.save()
                    ar.set_response(refresh_all=True)
        #~ return kw

    #~ def get_row_permission(self,user,state,ba):
        #~ """
        #~ """
        #~ logger.info("20121011 get_row_permission %s %s",self,ba)
        #~ if isinstance(ba.action,actions.SubmitInsert):
            #~ if not user.coaching_type:
                #~ return False
        #~ return super(Coaching,self).get_row_permission(user,state,ba)

    def full_clean(self, *args, **kw):
        if not self.start_date and not self.end_date:
            self.start_date = settings.SITE.today()
        if not self.type and self.user:
            self.type = self.user.coaching_type
        super(Coaching, self).full_clean(*args, **kw)

    #~ def save(self,*args,**kw):
        #~ super(Coaching,self).save(*args,**kw)

    def summary_row(self, ar, **kw):
        return [ar.href_to(self.client), " (%s)" % self.state.text]

    # def get_related_project(self):
    #     return self.client

    def get_change_owner(self, ar):
        return self.client

    def get_change_observers(self):
        return self.client.get_change_observers()

    # def get_notify_observers(self):
    #     yield self.user
    #     for u in settings.SITE.user_model.objects.filter(
    #             coaching_supervisor=True).exclude(email=''):
    #         yield u


dd.update_field(Coaching, 'start_date', verbose_name=_("Coached from"))
dd.update_field(Coaching, 'end_date', verbose_name=_("until"))
dd.update_field(
    Coaching, 'user', verbose_name=_("Coach"),
    related_name="%(app_label)s_%(class)s_set_by_user")



class ClientChecker(Checker):
    model = client_model

    def get_responsible_user(self, obj):
        return obj.get_primary_coach()



class ClientCoachingsChecker(ClientChecker):
    """Coached clients should not be obsolete.  Only coached clients
    should have active coachings

    """
    verbose_name = _("Check coachings")

    def get_plausibility_problems(self, obj, fix=False):
        if obj.client_state == ClientStates.coached:
            if obj.is_obsolete:
                yield (False, _("Both coached and obsolete."))
        if obj.client_state != ClientStates.coached:
            today = dd.today()
            period = (today, today)
            qs = obj.get_coachings(period)
            if qs.count():
                yield (False, _("Not coached, but with active coachings."))

ClientCoachingsChecker.activate()


class ClientContactType(mixins.BabelNamed):
    """A **client contact type** is the type or "role" which must be
    specified for a given :class:`ClientContact`.

    .. attribute:: can_refund

    Whether persons of this type can be used as doctor of a refund
    confirmation. Injected by :mod:`lino_welfare.modlib.aids`.

    """
    class Meta:
        app_label = 'coachings'
        verbose_name = _("Client Contact type")
        verbose_name_plural = _("Client Contact types")


class ClientContact(ClientContactBase):
    """A **client contact** is when a given partner has a given role for
    a given client.

    .. attribute:: client

    The :class:`Client`

    .. attribute:: company

    the Company

    .. attribute:: contact_person
    
    the Contact person in the Company

    .. attribute:: contact_role
    
    the role of the contact person in the Company

    .. attribute:: type
    
    The :class:`ClientContactType`.

    """
    class Meta:
        app_label = 'coachings'
        verbose_name = _("Client Contact")
        verbose_name_plural = _("Client Contacts")
    #~ type = ClientContactTypes.field(blank=True)
    client = dd.ForeignKey(client_model)
    remark = models.TextField(_("Remarks"), blank=True)  # ,null=True)

    def full_clean(self, *args, **kw):
        if not self.remark and not self.type \
           and not self.company and not self.contact_person:
            raise ValidationError(_("Must fill at least one field."))
        super(ClientContact, self).full_clean(*args, **kw)


dd.update_field(ClientContact, 'contact_person',
                verbose_name=_("Contact person"))


dd.inject_field(
    'users.User', 'coaching_type',
    dd.ForeignKey(
        'coachings.CoachingType',
        blank=True, null=True,
        help_text=_(
            "The coaching type used for new coachings with this user.")))

dd.inject_field(
    'users.User', 'coaching_supervisor',
    models.BooleanField(
        _("Coaching supervisor"),
        default=False,
        help_text=_("Notify me when a coach has been assigned")))

dd.inject_field(
    'contacts.Partner', 'client_contact_type',
    dd.ForeignKey(
        'coachings.ClientContactType', blank=True, null=True))

# contacts = dd.resolve_app('contacts')

from lino_xl.lib.contacts.models import Partners

class PartnersByClientContactType(Partners):
    master_key = 'client_contact_type'
    column_names = "name address_column phone gsm email *"
    auto_fit_column_widths = True

