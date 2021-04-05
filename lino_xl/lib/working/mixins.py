# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


# from django.db import models
# from django.utils import timezone

from lino.api import dd, rt, _

# from lino.mixins.periods import Monthly
# from lino.modlib.printing.mixins import DirectPrintAction
# from lino.core.roles import SiteUser
# from .roles import Worker
# from lino_xl.lib.tickets.roles import Triager

from .actions import StartTicketSession, EndTicketSession


class Workable(dd.Model):

    class Meta:
        abstract = True

    create_session_on_create = False

    def get_ticket(self):
        return self

    def is_workable_for(self, user):
        return True

    if dd.is_installed('working'):

        start_session = StartTicketSession()
        end_session = EndTicketSession()

        def disabled_fields(self, ar):
            s = super(Workable, self).disabled_fields(ar)
            user = ar.get_user()
            if not (user.is_authenticated and self.is_workable_for(user)):
                s.add('start_session')
                s.add('end_session')
                return s
            Session = rt.models.working.Session
            qs = Session.objects.filter(
                user=user, ticket=self.get_ticket(),
                end_time__isnull=True)
            if qs.exists():
                s.add('start_session')
            else:
                s.add('end_session')
            return s

        def save_new_instance(elem, ar):
            super(Workable, elem).save_new_instance(ar)

            if rt.settings.SITE.loading_from_dump or not dd.is_installed('working'):
                return
            me = ar.get_user()
            # print elem.create_session_on_create
            if elem.create_session_on_create and me is not None and me.open_session_on_new_ticket:
                ses = rt.models.working.Session(ticket=elem, user=me)
                ses.full_clean()
                ses.save()
