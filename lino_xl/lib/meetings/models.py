# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
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
from lino.utils.xmlgen.html import E, join_elems
from lino.mixins import Referrable

from lino.mixins.duplicable import Duplicable
from lino_xl.lib.tickets.mixins import Milestone

# from lino.mixins.periods import DatePeriod
# from lino_xl.lib.excerpts.mixins import Certifiable
# from lino_xl.lib.excerpts.mixins import ExcerptTitle
# from lino.modlib.users.mixins import UserAuthored
# from lino.modlib.printing.mixins import Printable
from lino.modlib.printing.utils import PrintableObject
from lino_xl.lib.cal.mixins import Reservation
# from lino_xl.lib.cal.choicelists import Recurrencies
# from lino_xl.lib.cal.utils import day_and_month
# from lino_xl.lib.contacts.mixins import ContactRelated

from lino.utils.dates import DatePeriodValue

from .choicelists import MeetingStates


@dd.python_2_unicode_compatible
class Meeting(Milestone, Reservation, Duplicable, PrintableObject):
    # """A Course is a group of pupils that regularily meet with a given
    # teacher in a given room to speak about a given subject.
    #
    # The subject of a course is expressed by the :class:`Line`.
    #
    # Notes about automatic calendar entry generation:
    #
    # - When an automatically generated entry is to be moved to another
    #   date, e.g. because it falls into a vacation period, then you
    #   simply change it's date.  Lino will automatically adapt all
    #   subsequent events.
    #
    # - Marking an automatically generated event as "Cancelled" will not
    #   create a replacement event.
    #
    # .. attribute:: enrolments_until
    #
    # .. attribute:: max_places
    #
    #     Available places. The maximum number of participants to allow
    #     in this course.
    #
    # .. attribute:: free_places
    #
    #     Number of free places.
    #
    # .. attribute:: requested
    #
    #     Number of requested places.
    #
    # .. attribute:: trying
    #
    #     Number of trying places.
    #
    # .. attribute:: confirmed
    #
    #     Number of confirmed places.
    #
    #
    # """
    workflow_state_field = 'state'

    class Meta:
        app_label = 'meetings'
        verbose_name = _("Meeting")
        verbose_name_plural = _('Meetings')
        # verbose_name = _("Event")
        # verbose_name_plural = _('Events')

    list = dd.ForeignKey('lists.List', verbose_name=_("Memebers"), blank=True, null=True)

    description = dd.BabelTextField(_("Description"), blank=True)

    remark = dd.RichTextField(_("Remark"), blank=True)

    quick_search_fields = 'name description remark'
    site_field_name = 'room'

    state = MeetingStates.field(
        default=MeetingStates.draft.as_callable)

    name = dd.CharField(_("Designation"), max_length=100, blank=True)

    def on_duplicate(self, ar, master):
        # self.state = CourseStates.draft
        super(Meeting, self).on_duplicate(ar, master)

    def __str__(self):
        if self.name:
            return self.name
        if self.room is None:
            return "(%s@%s)" % (self.members, dd.fds(self.start_date))
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
        if self.list:
            for obj in self.list.members.all():
                u = obj.partner.get_as_user()
                if u is not None:
                    yield u

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


@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`

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
        return E.tostring(e)

    sender.kernel.memo_parser.register_django_model(
        'meeting', Meeting,
        cmd=cmd,
        # title=lambda obj: obj.name
    )

