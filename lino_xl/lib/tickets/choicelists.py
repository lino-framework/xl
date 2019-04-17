# -*- coding: UTF-8 -*-
# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from django.utils.text import format_lazy
from django.db import models
from django.conf import settings

from lino.modlib.system.choicelists import (
    ObservedEvent, PeriodStarted, PeriodActive, PeriodEnded)

from lino.api import dd, pgettext, _
from lino_xl.lib.xl.choicelists import Priorities
from .roles import Triager

from datetime import datetime, time
combine = datetime.combine
T00 = time(0, 0, 0)
T24 = time(23, 59, 59)


class TicketEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")


class TicketEventCreated(ObservedEvent):
    text = _("Created")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(created__gte=combine(pv.start_date, T00))
        if pv.end_date:
            qs = qs.filter(created__lte=combine(pv.end_date, T24))
        return qs

TicketEvents.add_item_instance(TicketEventCreated('created'))


class TicketEventModified(ObservedEvent):
    text = _("Modified")

    def add_filter(self, qs, pv):
        if pv.start_date:
            qs = qs.filter(modified__gte=combine(pv.start_date, T00))
        if pv.end_date:
            qs = qs.filter(modified__lte=combine(pv.end_date, T24))
        return qs


TicketEvents.add_item_instance(TicketEventModified('modified'))


# class ProjectEvents(dd.ChoiceList):
#     verbose_name = _("Observed event")
#     verbose_name_plural = _("Observed events")
    
# ProjectEvents.add_item_instance(PeriodStarted('started'))
# ProjectEvents.add_item_instance(PeriodActive('active'))
# ProjectEvents.add_item_instance(PeriodEnded('ended'))
# ProjectEvents.add_item_instance(TicketEventModified('modified'))


class SiteState(dd.State):
    is_exposed = False
    
class SiteStates(dd.Workflow):
    verbose_name_plural = _("Site states")
    item_class = SiteState
    column_names = "value name text button_text is_exposed"
    is_exposed = models.BooleanField(_("Exposed"), default=False)

add = SiteStates.add_item
add('10', _("Draft"), 'draft', is_exposed=True,
    button_text = "⛶")  # SQUARE FOUR CORNERS (U+26F6))
add('20', _("Active"), 'active', is_exposed=True,
    button_text = "⚒")  # HAMMER AND PICK (U+2692
add('30', _("Stable"), 'stable', is_exposed=True,
    button_text = "☉")  # SUN (U+2609)	
add('40', _("Sleeping"), 'sleeping',
    button_text = "☾")  # LAST QUARTER MOON (U+263E)
add('50', _("Closed"), 'closed',
    button_text = "☑")  # BALLOT BOX WITH CHECK \u2611)

SiteStates.draft.add_transition()
SiteStates.active.add_transition()
SiteStates.stable.add_transition()
SiteStates.sleeping.add_transition()
SiteStates.closed.add_transition()

    
class TicketState(dd.State):
    active = False
    show_in_todo = False
    
    def get_summary_field(self):
        return self.name + '_tickets'
        # return 'tickets_in_' + self.name
   
class TicketStates(dd.Workflow):

    # verbose_name = _("Ticket state")
    verbose_name_plural = _("Ticket states")
    item_class = TicketState
    column_names = "value name text button_text active"
    active = models.BooleanField(_("Active"), default=False)
    show_in_todo = models.BooleanField(_("To do"), default=False)
    required_roles = dd.login_required(dd.SiteStaff)
    # max_length = 3

add = TicketStates.add_item

add('10', _("New"), 'new', active=True, show_in_todo=True)
add('15', _("Talk"), 'talk', active=True)
add('20', pgettext("ticket state", "Open"), 'opened', active=True, show_in_todo=True)
# add('21', _("Sticky"), 'sticky', active=True)
# add('22', _("Started"), 'started', active=True, show_in_todo=True)
add('22', _("Working"), 'working', active=True, show_in_todo=True)
add('30', _("Sleeping"), 'sleeping')
add('40', _("Ready"), 'ready', active=True)
add('50', _("Closed"), 'closed')
add('60', _("Refused"), 'cancelled')
# TicketStates.default_value = 'new'


if settings.SITE.use_new_unicode_symbols:

    TicketStates.new.button_text =u"📥"  # INBOX TRAY (U+1F4E5)
    TicketStates.talk.button_text =u"🗪"  # TWO SPEECH BUBBLES (U+1F5EA)
    TicketStates.opened.button_text = u"☉"  # SUN (U+2609)	
    TicketStates.working.button_text=u"🐜"  # ANT (U+1F41C)
    TicketStates.cancelled.button_text=u"🗑"  # WASTEBASKET (U+1F5D1)
    # TicketStates.sticky.button_text=u"📌"  # PUSHPIN (U+1F4CC)
    TicketStates.sleeping.button_text = u"🕸"  # SPIDER WEB (U+1F578)	
    TicketStates.ready.button_text = "\u2610"  # BALLOT BOX
    TicketStates.closed.button_text = "\u2611"  # BALLOT BOX WITH CHECK

else:    
    TicketStates.new.button_text = "⛶"  # SQUARE FOUR CORNERS (U+26F6)
    # TicketStates.talk.button_text = "⚔"  # CROSSED SWORDS (U+2694)
    TicketStates.talk.button_text = "☎"  # Black Telephone (U+260E)
    TicketStates.opened.button_text = "☉"  # SUN (U+2609)	
    # TicketStates.working.button_text="☭"  # HAMMER AND SICKLE (U+262D)
    TicketStates.working.button_text = "⚒"  # HAMMER AND PICK (U+2692
    # TicketStates.sticky.button_text="♥"  # BLACK HEART SUIT (U+2665)
    # TicketStates.sticky.button_text="♾"  # (U+267E)
    TicketStates.sleeping.button_text = "☾"  # LAST QUARTER MOON (U+263E)
    TicketStates.ready.button_text = "☐"  # BALLOT BOX \u2610
    TicketStates.closed.button_text = "☑"  # BALLOT BOX WITH CHECK \u2611
    TicketStates.cancelled.button_text="☒"  # BALLOT BOX WITH X (U+2612)


class LinkType(dd.Choice):

    symmetric = False

    def __init__(self, value, name, ptext, ctext, **kw):
        self.ptext = ptext  # parent
        self.ctext = ctext
        # text = string_concat(ptext, ' (', ctext, ')')
        text = ptext
        super(LinkType, self).__init__(value, text, name, **kw)

    def as_parent(self):
        return self.ptext

    def as_child(self):
        return self.ctext


class LinkTypes(dd.ChoiceList):
    required_roles = dd.login_required(dd.SiteStaff)
    verbose_name = _("Dependency type")
    verbose_name_plural = _("Dependency types")
    item_class = LinkType

add = LinkTypes.add_item
add('10', 'requires', _("Requires"), _("Required by"))
add('20', 'triggers', _("Triggers"), _("Triggered by"))
add('30', 'suggests', _("Suggests"), _("Suggested by"))
add('40', 'obsoletes', _("Obsoletes"), _("Obsoleted by"))
# add('30', 'seealso', _("See also"), _("Referred by"))
# deprecated (use "fixed_for" field instead):
# add('40', 'deploys', _("Deploys"), _("Deployed by"))
# replaced by FK field "duplicate_of"):
# add('50', 'duplicates', _("Duplicates"), _("Duplicate of"))

# LinkTypes.addable_types = [LinkTypes.requires, LinkTypes.duplicates]


