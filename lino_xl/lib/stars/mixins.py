# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from builtins import str
from django.conf import settings
from lino.api import dd, rt, _
from lino.utils.xmlgen.html import E
from lino.modlib.office.roles import OfficeUser
from lino.modlib.notify.mixins import ChangeObservable



def get_favourite(obj, user):
    if user.authenticated:
        qs = rt.modules.stars.Star.for_obj(obj, user=user)
        if qs.count() == 0:
            return None
        return qs[0]


class StarObject(dd.Action):
    sort_index = 100
    # label = "*"
    label = u"☆"  # 2606
    help_text = _("Star this database object.")
    show_in_workflow = True
    show_in_bbar = False
    required_roles = dd.login_required(OfficeUser)

    def get_action_permission(self, ar, obj, state):
        star = get_favourite(obj, ar.get_user())
        if star is not None:
            return False
        return super(StarObject, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        Star = rt.modules.stars.Star
        Star(owner=obj, user=ar.get_user()).save()
        ar.success(
            _("{0} is now starred.").format(obj), refresh_all=True)


class UnstarObject(dd.Action):
    sort_index = 100
    # label = "-"
    label = u"★"  # 2605

    help_text = _("Unstar this database object.")
    show_in_workflow = True
    show_in_bbar = False

    def get_action_permission(self, ar, obj, state):
        star = get_favourite(obj, ar.get_user())
        if star is None:
            return False
        return super(UnstarObject, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        star = get_favourite(obj, ar.get_user())
        star.delete()
        ar.success(
            _("{0} is no longer starred.").format(obj), refresh_all=True)


class Starrable(ChangeObservable):

    class Meta(object):
        abstract = True

    if dd.is_installed("stars"):

        star_object = StarObject()
        unstar_object = UnstarObject()

        def get_change_observers(self):
            for o in super(Starrable, self).get_change_observers():
                yield o
            for star in rt.models.stars.Star.for_obj(self):
                yield (star.user, star.user.mail_mode)
