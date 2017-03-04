# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.db import models

from lino.api import dd, _
from lino import mixins

from lino.modlib.users.mixins import My
from .roles import CoachingsUser, CoachingsStaff
from .choicelists import *

contacts = dd.resolve_app('contacts')



class CoachingTypes(dd.Table):
    model = 'coachings.CoachingType'
    column_names = 'name does_integ does_gss eval_guestrole *'
    required_roles = dd.login_required(CoachingsStaff)


class CoachingEndings(dd.Table):
    help_text = _("A list of reasons expressing why a coaching was ended")
    required_roles = dd.login_required(CoachingsStaff)
    model = 'coachings.CoachingEnding'
    column_names = 'seqno name type *'
    order_by = ['seqno']
    detail_layout = """
    id name seqno
    CoachingsByEnding
    """

class Coachings(dd.Table):
    required_roles = dd.login_required(CoachingsStaff)
    help_text = _("Liste des accompagnements.")
    model = 'coachings.Coaching'

    parameters = mixins.ObservedPeriod(
        coached_by=models.ForeignKey(
            'users.User',
            blank=True, null=True,
            verbose_name=_("Coached by"),
            help_text="""Nur Begleitungen dieses Benutzers."""),
        and_coached_by=models.ForeignKey(
            'users.User',
            blank=True, null=True,
            verbose_name=_("and by"),
            help_text="""... und auch Begleitungen dieses Benutzers."""),
        observed_event=dd.PeriodEvents.field(
            blank=True, default=dd.PeriodEvents.active.as_callable),
        primary_coachings=dd.YesNo.field(
            _("Primary coachings"),
            blank=True, help_text="""Accompagnements primaires."""),
        coaching_type=models.ForeignKey(
            'coachings.CoachingType',
            blank=True, null=True,
            help_text="""Nur Begleitungen dieses Dienstes."""),
        ending=models.ForeignKey(
            'coachings.CoachingEnding',
            blank=True, null=True,
            help_text="""Nur Begleitungen mit diesem Beendigungsgrund."""),
    )
    params_layout = """
    start_date end_date observed_event coached_by and_coached_by
    primary_coachings coaching_type ending
    """
    params_panel_hidden = True

    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(Coachings,self).param_defaults(ar,**kw)
        #~ D = datetime.date
        #~ kw.update(start_date = D.today())
        #~ kw.update(end_date = D.today())
        #~ return kw

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Coachings, self).get_request_queryset(ar)
        pv = ar.param_values
        coaches = []
        for u in (pv.coached_by, pv.and_coached_by):
            if u is not None:
                coaches.append(u)
        if len(coaches):
            qs = qs.filter(user__in=coaches)

        ce = pv.observed_event
        if ce is not None:
            qs = ce.add_filter(qs, pv)

        if pv.primary_coachings == dd.YesNo.yes:
            qs = qs.filter(primary=True)
        elif pv.primary_coachings == dd.YesNo.no:
            qs = qs.filter(primary=False)
        if pv.coaching_type is not None:
            qs = qs.filter(type=pv.coaching_type)
        if pv.ending is not None:
            qs = qs.filter(ending=pv.ending)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Coachings, self).get_title_tags(ar):
            yield t

        pv = ar.param_values

        if pv.observed_event:
            yield unicode(pv.observed_event)

        if pv.coached_by:
            s = unicode(self.parameters['coached_by'].verbose_name) + \
                ' ' + unicode(pv.coached_by)
            if pv.and_coached_by:
                s += " %s %s" % (unicode(_('and')),
                                 pv.and_coached_by)
            yield s

        if pv.primary_coachings:
            yield unicode(self.parameters['primary_coachings'].verbose_name) \
                + ' ' + unicode(pv.primary_coachings)

    @classmethod
    def get_create_permission(self, ar):
        """Reception clerks can see coachings, but cannot modify them nor add
        new ones.

        """
        
        if not ar.get_user().profile.has_required_roles([CoachingsUser]):
        #if not ar.get_user().profile.coaching_level:
            return False
        return super(Coachings, self).get_create_permission(ar)


class CoachingsByClient(Coachings):
    """
    The :class:`Coachings` table in a :class:`Clients` detail.
    """
    required_roles = dd.login_required()
    #~ debug_permissions = 20121016
    master_key = 'client'
    order_by = ['start_date']
    column_names = 'start_date end_date user:12 primary type:12 ending id'
    hidden_columns = 'id'
    auto_fit_column_widths = True


class CoachingsByEnding(Coachings):
    master_key = 'ending'


class CoachingsByUser(Coachings):
    required_roles = dd.login_required(CoachingsUser)
    master_key = 'user'
    column_names = 'start_date end_date client type primary id'


class MyCoachings(My, CoachingsByUser):
    column_names = 'client start_date end_date type primary id'
    order_by = ['client__name']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyCoachings, self).param_defaults(ar, **kw)
        kw.update(start_date=dd.today())
        kw.update(end_date=dd.today())
        return kw


class ClientContactTypes(dd.Table):
    help_text = _("Liste des types de contacts client.")
    model = 'coachings.ClientContactType'
    required_roles = dd.login_required(CoachingsStaff)

    # TODO: `can_refund` is injected in aids, `is_bailiff` in debts
    # NOTE: this is being overridden by lino_welfare.projects.eupen
    detail_layout = """
    id name
    coachings.PartnersByClientContactType
    coachings.ClientContactsByType
    """

    column_names = 'id name *'

    stay_in_grid = True


class ClientContacts(dd.Table):
    required_roles = dd.login_required(CoachingsStaff)
    help_text = _("Liste des contacts clients.")
    model = 'coachings.ClientContact'


class ContactsByClient(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'client'
    column_names = 'type company contact_person remark *'
    label = _("Contacts")
    auto_fit_column_widths = True


class ClientContactsByType(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'type'
    column_names = 'company contact_person client remark *'
    label = _("Contacts")
    auto_fit_column_widths = True


class ClientContactsByCompany(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'company'
    column_names = 'client contact_person remark *'
    label = _("Clients contacts")
    auto_fit_column_widths = True


class PartnersByClientContactType(contacts.Partners):
    master_key = 'client_contact_type'
    column_names = 'name id mti_navigator *'


