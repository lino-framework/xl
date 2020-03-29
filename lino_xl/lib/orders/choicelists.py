# -*- coding: UTF-8 -*-
# Copyright 2019-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models

from lino_xl.lib.ledger.choicelists import VoucherStates
from lino.api import dd, _


class OrderStates(VoucherStates):
    pass

add = OrderStates.add_item
add('10', _("Waiting"), 'draft', is_editable=True)
add('20', _("Active"), 'active', is_editable=True)
add('30', _("Urgent"), 'urgent', is_editable=True)
add('40', _("Done"), 'registered')
add('50', _("Cancelled"), 'cancelled')

OrderStates.draft.add_transition(required_states="active urgent registered cancelled")
OrderStates.active.add_transition(required_states="draft urgent registered cancelled")
OrderStates.urgent.add_transition(required_states="draft active registered cancelled")
OrderStates.registered.add_transition(required_states="draft active urgent cancelled")
OrderStates.cancelled.add_transition(required_states="draft active urgent registered")
