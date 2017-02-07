# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""Model mixins for this plugin.

"""

from django.conf import settings

from lino.api import dd, rt, _
from lino.utils.xmlgen.html import E

from lino.modlib.notify.mixins import ChangeObservable
from lino_xl.lib.contacts.mixins import ContactRelated

from .choicelists import ClientStates
from .utils import only_active_coachings_filter


class Coachable(ChangeObservable):
    """Base class for coachable client.

    """

    class Meta:
        abstract = True

    workflow_state_field = 'client_state'

    client_state = ClientStates.field(
        default=ClientStates.newcomer.as_callable)

    def get_coachings(self, period=None, *args, **flt):
        """"Return a queryset with the coachings of this client. If `period`
        is not None, it must be a tuple of two date objects. Any
        additional arguments are applied as filter of the queryset.

        """
        qs = self.coachings_by_client.filter(*args, **flt)
        if period is not None:
            qs = qs.filter(only_active_coachings_filter(period))
        return qs

    def get_primary_coach(self):
        """Return the one and only primary coach of this client (or `None` if
        there's less or more than one).

        """
        qs = self.coachings_by_client.filter(primary=True).distinct()
        if qs.count() == 1:
            return qs[0].user
        # logger.info("20140725 qs is %s", qs)
        return None

    @dd.displayfield(_('Primary coach'))
    def primary_coach(self, ar=None):
        return self.get_primary_coach()

    # primary_coach = property(get_primary_coach)

    @dd.displayfield(_("Coaches"))
    def coaches(self, ar):
        today = dd.today()
        period = (today, today)
        items = [unicode(obj.user) for obj in self.get_coachings(period)]
        return ', '.join(items)

    def get_change_observers(self):
        for u in settings.SITE.user_model.objects.filter(
                coaching_supervisor=True):
            yield (u, u.mail_mode)
        today = dd.today()
        period = (today, today)
        for obj in self.get_coachings(period):
            yield (obj.user, obj.user.mail_mode)


    @dd.displayfield(_("Find appointment"))
    def find_appointment(self, ar):
        if ar is None:
            return ''
        CalendarPanel = rt.actors.extensible.CalendarPanel
        elems = []
        for obj in self.coachings_by_client.all():
            sar = CalendarPanel.request(
                subst_user=obj.user, current_project=self.pk)
            elems += [ar.href_to_request(sar, obj.user.username), ' ']
        return E.div(*elems)


@dd.python_2_unicode_compatible
class ClientContactBase(ContactRelated):
    """Also used by :class:`aids.RefundPartner
    <lino_welfare.modlib.aids.models.RefundPartner>`.

    """

    class Meta:
        abstract = True
    type = dd.ForeignKey(
        'coachings.ClientContactType', blank=True, null=True)

    @dd.chooser()
    def company_choices(self, type):
        qs = rt.modules.contacts.Companies.request().data_iterator
        if type is not None:
            qs = qs.filter(client_contact_type=type)
        return qs

    @dd.chooser()
    def contact_person_choices(self, type):
        qs = rt.modules.contacts.Persons.request().data_iterator
        if type is not None:
            qs = qs.filter(client_contact_type=type)
        return qs

    def __str__(self):
        return unicode(self.contact_person or self.company or self.type)

