# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

"""
Choicelists for this plugin.

"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd


class MeetingStates(dd.Workflow):
    required_roles = dd.login_required(dd.SiteAdmin)

add = MeetingStates.add_item
add('10', _("Draft"), 'draft',
    editable=True, active=True)
add('20', _("Started"), 'active',
    editable=True, active=True)
#Set to editable=True since you can't duplicate on a read-only
add('30', _("Inactive"), 'inactive',
    editable=True, active=False)
add('40', _("Finished"), 'closed',
    editable=True, active=False)

