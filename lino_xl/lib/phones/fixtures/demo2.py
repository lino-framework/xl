# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""

"""

from lino.api import rt


def objects():

    from lino_xl.lib.phones.mixins import ContactDetailsOwner
    for m in rt.models_by_base(ContactDetailsOwner):
        for p in m.objects.all():
            p.propagate_contact_details()
            yield p
