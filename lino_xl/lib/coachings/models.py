# -*- coding: UTF-8 -*-
# Copyright 2008-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import logging ; logger = logging.getLogger(__name__)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from lino.api import dd, rt

from lino import mixins

from lino.modlib.users.mixins import UserAuthored
from lino.modlib.notify.mixins import ChangeNotifier
from lino.modlib.checkdata.choicelists import Checker

from lino_xl.lib.clients.choicelists import ClientStates
from .roles import CoachingsStaff
from .mixins import ClientChecker

from lino.modlib.notify.choicelists import MessageTypes
MessageTypes.add_item('coachings', dd.plugins.coachings.verbose_name)


try:
    client_model = dd.plugins.clients.client_model
except AttributeError:  # for Sphinx autodoc
    client_model = None

INTEG_LABEL = _("Integration")
GSS_LABEL = _("GSS")  # General Social Service


class CoachingType(mixins.BabelNamed):

    class Meta:
        app_label = 'coachings'
        verbose_name = _("Coaching type")
        verbose_name_plural = _('Coaching types')
        abstract = dd.is_abstract_model(__name__, 'CoachingType')

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
        abstract = dd.is_abstract_model(__name__, 'CoachingEnding')

    #~ name = models.CharField(_("designation"),max_length=200)
    type = dd.ForeignKey(
        CoachingType,
        blank=True, null=True,
        help_text=_("If not empty, allow this ending only on "
                    "coachings of specified type."))


class Coaching(UserAuthored, mixins.DateRange, dd.ImportedFields, ChangeNotifier):

    class Meta:
        app_label = 'coachings'
        verbose_name = _("Coaching")
        verbose_name_plural = _("Coachings")
        abstract = dd.is_abstract_model(__name__, 'Coaching')

    # user = dd.ForeignKey(
    #     settings.SITE.user_model,
    #     verbose_name=_("Coach"),
    #     related_name="%(app_label)s_%(class)s_set_by_user",
    # )

    allow_cascaded_delete = ['client']
    workflow_state_field = 'state'
    manager_roles_required = dd.login_required(CoachingsStaff)

    client = dd.ForeignKey(client_model, related_name="coachings_by_client")
    type = dd.ForeignKey('coachings.CoachingType', blank=True, null=True)
    primary = models.BooleanField(_("Primary"), default=False)

    ending = dd.ForeignKey(
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

    # def disabled_fields(self, ar):
    #     rv = super(Coaching, self).disabled_fields(ar)
    #     if settings.SITE.is_imported_partner(self.client):
    #         if self.primary:
    #             rv |= self._imported_fields
    #         rv.add('primary')
    #     return rv

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
        if not self.client_id:
            return super(Coaching, self).__str__()
        cl = self.client
        if self.user_id is None:
            return "{} {}".format(
                self.__class__._meta.verbose_name, cl)
        if cl.first_name:
            return self.user.username + ' / ' + cl.last_name + ' ' + cl.first_name[0]
        return self.user.username + ' / ' + cl.last_name

    def adapt_primary(self):
        if self.primary:
            qs = self.client.coachings_by_client.exclude(id=self.id)
            if dd.plugins.coachings.multiple_primary_coachings:
                qs = qs.filter(type=self.type)
            for c in qs:
                if c.primary:
                    c.primary = False
                    c.save()
                    return True

    def after_ui_save(self, ar, cw):
        super(Coaching, self).after_ui_save(ar, cw)
        if self.adapt_primary():
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

    def get_change_owner(self):
        return self.client

    # def get_notify_message_type(self):
    #     return rt.models.notify.MessageTypes.coachings

    # def get_change_observers(self, ar=None):
    #     return self.client.get_change_observers(ar)

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





class ClientCoachingsChecker(ClientChecker):
    verbose_name = _("Check coachings")

    def get_checkdata_problems(self, obj, fix=False):
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


dd.inject_field(
    'users.User', 'coaching_type',
    dd.ForeignKey(
        'coachings.CoachingType',
        blank=True, null=True))

dd.inject_field(
    'users.User', 'coaching_supervisor',
    models.BooleanField(
        _("Coaching supervisor"),
        default=False))
