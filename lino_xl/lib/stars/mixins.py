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

# NOTE: Do we want to perhaps have this in change_watchers rather then here?
class CascadeStars(dd.Action):
    """
    Gathers a list of childen models that want to have all the stars that are in the parent, then add them.

    Used when adding a new star to a high-level object. Done in separate action for safety.
    """
    sort_index = 100
    label = u"★"  # 2605
    help_text = _("Cascade Stars to all objects under this model")
    # show_in_workflow = True
    show_in_bbar = True
    required_roles = dd.login_required(OfficeUser)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        # stars = obj.get_stars()
        users = [s.user for s in obj.get_stars()]
        for o in obj.get_children_starrable(ar):
            if o.stars_cascade:
                for u in users:
                    star = get_favourite(o, user=u)
                    if star is None:
                        Star = rt.modules.stars.Star
                        star = Star(owner=o, user=u)
                        star.save()
                    # o.add_change_watcher(u)
        #todo: Better return message?
        # ar.success(
        #     _("{0} is no longer starred.").format(obj), refresh_all=True)


class Starrable(ChangeObservable):

    class Meta(object):
        abstract = True

    stars_cascade = True
    """
    If true the CascadeStars action will not add stars to this model, even if it is a child
    """

    if dd.is_installed("stars"):

        star_object = StarObject()
        unstar_object = UnstarObject()

        def get_change_observers(self):
            for o in super(Starrable, self).get_change_observers():
                yield o
            for star in self.get_stars():
                yield (star.user, star.user.mail_mode)

        def get_stars(self):
            for star in rt.models.stars.Star.for_obj(self):
                yield star

class Starrable_Tree(Starrable):
    class Meta(object):
        abstract = True
    stars_cascade = True

    if dd.is_installed("stars"):

        cascade_stars = CascadeStars()

        def get_children_starrable(self, ar):
            raise NotImplementedError()
