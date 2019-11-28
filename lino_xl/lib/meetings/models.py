# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""Database models for `lino_xl.lib.meetings`.

"""

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

"""Database models for :mod:`lino_xl.lib.meetings`.

.. autosummary::

"""

import logging

logger = logging.getLogger(__name__)

from lino.api import dd, rt, _
from etgen.html import tostring
from django.db.models import Q
from lino.mixins import Referrable

from lino.mixins.duplicable import Duplicable
from lino_xl.lib.tickets.mixins import Milestone

# from lino.mixins.periods import DateRange
# from lino_xl.lib.excerpts.mixins import Certifiable
# from lino_xl.lib.excerpts.mixins import ExcerptTitle
# from lino.modlib.users.mixins import UserAuthored
from django.utils.text import format_lazy
from lino_xl.lib.cal.mixins import Reservation
from lino_xl.lib.stars.mixins import Starrable
# from lino_xl.lib.cal.choicelists import Recurrencies
# from lino_xl.lib.cal.utils import day_and_month
# from lino_xl.lib.contacts.mixins import ContactRelated

from datetime import datetime
from lino.utils.dates import DateRangeValue

from .choicelists import MeetingStates
from lino_xl.lib.tickets.choicelists import TicketStates



class Meeting(Referrable, Milestone, Reservation, Duplicable, Starrable):
    """A Meetings is a list of tickets that are to be discussed with a group of people
    """
    # .. attribute:: max_places
    #
    #     Available places. The maximum number of participants to allow
    #     in this course.
    #
    # """
    workflow_state_field = 'state'

    class Meta:
        app_label = 'meetings'
        verbose_name = _("Meeting")
        verbose_name_plural = _('Meetings')
        # verbose_name = _("Event")
        # verbose_name_plural = _('Events')

    description = dd.RichTextField(_("Description"), blank=True)

    child_starrables = [('deploy.Deployment','milestone','ticket')]

    quick_search_fields = 'name description ref'
    site_field_name = 'site'

    site = dd.ForeignKey('tickets.Site', blank=True, null=True)

    state = MeetingStates.field(
        default=MeetingStates.as_callable('draft'))

    name = dd.CharField(_("Title"), max_length=100, blank=True)

    def on_duplicate(self, ar, master):
        # self.state = CourseStates.draft
        # def OK(ar):
        self.state = MeetingStates.draft
        # ar.confirm(OK,_("Remove inactive tickets on new meeting?"))
        old = ar.selected_rows[0]
        if self.ref:
            old.ref = datetime.now().strftime("%Y%m%d") + "@" + old.ref
            old.full_clean()
            old.save()
        super(Referrable, self).on_duplicate(ar, master)

    def after_duplicate(self, ar, master):
        rt.models.deploy.Deployment.objects.filter(Q(milestone=self),
                                               Q(new_ticket_state__in=TicketStates.filter(active=False)) | Q(ticket__state__in=TicketStates.filter(active=False))
                                               ).delete()
        rt.models.deploy.Deployment.objects.filter(milestone=self).update(
            new_ticket_state=None,
            old_ticket_state=None,
            remark="",
        )
        stars = rt.models.stars.Star.for_obj(master,) #no master__isnull since we want to copy the site star
        for s in stars:
            s.owner = self
            s.id = None
            s.save()

    def __str__(self):
        if self.ref:
            return self.ref
        if self.name:
            return self.name
        if self.room is None:
            return "(%s)" % (dd.fds(self.start_date))
        # Note that we cannot use super() with
        # python_2_unicode_compatible
        return "(%s@%s)" % (
            dd.fds(self.start_date),
            self.room)

    def update_cal_from(self, ar):
        """Note: if recurrency is weekly or per_weekday, actual start may be
        later than self.start_date

        """
        return self.start_date

    def update_cal_event_type(self):
        return None


    def full_clean(self, *args, **kw):
        super(Meeting, self).full_clean(*args, **kw)

    def get_milestone_users(self):
        #todo
        if dd.is_installed("stars"):
            for s in rt.models.stars.Star.for_obj(self):
                # u = obj.partner.get_as_user()
                # if u is not None:
                yield s.user

    def site_changed(self, ar):
        """Leaves a sub-star of old site, but that's OK for now"""
        if self.site is not None:
            self.site.add_child_stars(self.site, self)
            # self.add_change_watcher(star.user)

    def after_ui_create(self, ar):
        self.site_changed(ar)
        super(Meeting, self).after_ui_create(ar)


    @classmethod
    def add_param_filter(
            cls, qs, lookup_prefix='', show_active=None, **kwargs):
        qs = super(Meeting, cls).add_param_filter(qs, **kwargs)
        active_states = MeetingStates.filter(active=True)
        fkw = dict()
        fkw[lookup_prefix + 'state__in'] = active_states
        if show_active == dd.YesNo.no:
            qs = qs.exclude(**fkw)
        elif show_active == dd.YesNo.yes:
            qs = qs.filter(**fkw)
        return qs

    @classmethod
    def quick_search_filter(model, search_text, prefix=''):
        q = Q()
        if search_text.isdigit():
            for fn in model.quick_search_fields:
                kw = {prefix + fn.name + "__icontains": search_text}
                q = q | Q(**kw)
            return q
        #Skip referable's method
        return super(Referrable, model).quick_search_filter(search_text, prefix)


@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`

    if not sender.is_installed('memo'):
        return

    Meeting = sender.models.meetings.Meeting

    def cmd(parser, s):
        pk = s
        txt = None

        ar = parser.context['ar']
        kw = dict()
        # dd.logger.info("20161019 %s", ar.renderer)
        pk = int(pk)
        obj = Meeting.objects.get(pk=pk)
        # try:
        # except model.DoesNotExist:
        #     return "[{} {}]".format(name, s)
        if txt is None:
            txt = "{0}".format(obj.name)
            kw.update(title=obj.name)
        e = ar.obj2html(obj, txt, **kw)
        # return str(ar)
        return tostring(e)

    sender.plugins.memo.parser.register_django_model(
        'meeting', Meeting,
        cmd=cmd,
        # title=lambda obj: obj.name
    )

