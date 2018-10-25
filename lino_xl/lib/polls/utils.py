# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.utils.translation import ugettext_lazy as _
from lino.mixins import RegistrableState
from lino.api import dd

class PollStates(dd.Workflow):
    item_class = RegistrableState
    verbose_name_plural = _("Poll states")
    required_roles = dd.login_required(dd.SiteStaff)


add = PollStates.add_item
add('10', _("Draft"), 'draft')
add('20', _("Active"), 'active')
add('30', _("Closed"), 'closed')

PollStates.active.add_transition(
    _("Publish"), required_states='draft')
PollStates.closed.add_transition(
    _("Close"), required_states='draft active')
PollStates.draft.add_transition(
    _("Reopen"), required_states='active closed')


class ResponseStates(dd.Workflow):
    item_class = RegistrableState
    verbose_name_plural = _("Response states")
    required_roles = dd.login_required(dd.SiteStaff)


add = ResponseStates.add_item
add('10', _("Draft"), 'draft', is_editable=True)
add('20', _("Registered"), 'registered', is_editable=False)


ResponseStates.registered.add_transition(
    _("Register"), required_states='draft')
ResponseStates.draft.add_transition(
    _("Deregister"), required_states="registered")


