# -*- coding: UTF-8 -*-
# Copyright 2014-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, rt, _

from lino.utils.mldbc import babeld


def objects():
    ListType = rt.models.lists.ListType
    List = rt.models.lists.List

    mailing = babeld(ListType, _("Mailing list"))
    yield mailing

    discuss = babeld(ListType, _("Discussion group"))
    yield discuss

    flags = ListType(**dd.str2kw('designation', _("Flags")))
    yield flags

    yield List(list_type=mailing, **dd.str2kw('designation', _("Announcements")))
    yield List(list_type=mailing, **dd.str2kw('designation', _("Weekly newsletter")))

    yield List(list_type=discuss, **dd.str2kw('designation', _("General discussion")))
    yield List(list_type=discuss, **dd.str2kw('designation', _("Beginners forum")))
    yield List(list_type=discuss, **dd.str2kw('designation', _("Developers forum")))

    yield List(list_type=flags,
               **dd.str2kw('designation', _("PyCon 2014")))
    yield List(list_type=flags,
               **dd.str2kw('designation', _("Free Software Day 2014")))
    yield List(list_type=flags, **dd.str2kw('designation', _("Schools")))
