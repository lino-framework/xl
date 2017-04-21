# -*- coding: UTF-8 -*-
# Copyright 2012-2017 Luc Saffre
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

"""Importing this module will install default workflows for
`lino_xl.lib.meetings`.

"""

from lino.api import dd, rt, _

from .choicelists import MeetingStates

#
# @dd.receiver(dd.pre_analyze)
# def my_enrolment_workflows(sender=None, **kw):

MeetingStates.active.add_transition(
    required_states="draft inactive")
MeetingStates.draft.add_transition(
    required_states="active inactive closed")
MeetingStates.inactive.add_transition(
    required_states="draft active")
MeetingStates.closed.add_transition(
    required_states="draft active inactive")
