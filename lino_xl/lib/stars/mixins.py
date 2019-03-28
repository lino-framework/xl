# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

from builtins import str
from django.conf import settings
from lino.api import dd, rt, _
from etgen.html import E
from lino.modlib.office.roles import OfficeUser
from lino.modlib.notify.mixins import ChangeNotifier
from six import string_types
from django.db import IntegrityError

def get_favourite(obj, user, **kws):
    if user.authenticated:
        qs = rt.models.stars.Star.for_obj(obj, user=user,**kws)
        # if qs.count() == 0:
        #     return None
        # return qs[0]
        return qs.first()


class StarObject(dd.Action):
    sort_index = 100
    # label = "*"
    label = u"☆"  # 2606
    help_text = _("Star this database object.")
    show_in_workflow = True
    show_in_bbar = False
    required_roles = dd.login_required(OfficeUser)

    # def get_action_permission(self, ar, obj, state):
    #     star = get_favourite(obj, ar.get_user())
    #     if star is not None:
    #         return False
    #     return super(StarObject, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        Star = rt.models.stars.Star
        obj = ar.selected_rows[0]
        Star.create_star(obj, ar)
        ar.success(
            _("{0} is now starred.").format(obj), refresh_all=True)

    # def create_star(self, obj, ar):
    #     Star = rt.models.stars.Star
    #     Star(owner=obj, user=ar.get_user()).save()

class FullStarObject(StarObject):

    label = u"✫"  #10031 u+272f ✫
    # 9956 U+26e4 ⛤
    # 10027 U+272b ✯
    # 10031 u+272f ✫
    help_text = _("Star this database object fully.")

    # def get_action_permission(self, ar, obj, state):
    #     user = ar.get_user()
    #     if user.authenticated:
    #         master_star_qs = rt.models.stars.Star.for_obj(obj, user=user, master__isnull=True)
    #         child_star_qs = rt.models.stars.Star.for_obj(obj, user=user)
    #         if not (master_star_qs.count() == 0 and child_star_qs.count()):
    #             return False
    #     else:
    #         return False
    #     return super(StarObject, self).get_action_permission(ar, obj, state) #Skip StarObject method

class UnstarObject(dd.Action):
    "Unstar this database object."
    
    sort_index = 100
    # label = "-"
    label = u"★"  # 2605

    show_in_workflow = True
    show_in_bbar = False

    # def get_action_permission(self, ar, obj, state):
    #     user = ar.get_user()
    #     if user.authenticated:
    #         master_star_qs = rt.models.stars.Star.for_obj(obj, user=user, master__isnull=True)
    #         if not (master_star_qs.count()):
    #             return False
    #     else:
    #         return False
    #     return super(UnstarObject, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        self.delete_star(obj, ar)
        ar.success(
            _("{0} is no longer starred.").format(obj), refresh_all=True)

    def delete_star(self, obj, ar):
        user = ar.get_user()
        # children_star_qs = rt.models.stars.Star.for_master(obj, user=user)
        # star = get_favourite(obj, ar.get_user())
        # children_star_qs.delete()
        # ON cascade delete?
        master_star_qs = rt.models.stars.Star.for_obj(obj, user=user, master__isnull=True)
        master_star_qs.delete()

class Starrable(ChangeNotifier):

    class Meta(object):
        abstract = True

    child_starrables = []
    """
    A list of (model, master-key, related_field) tuples for child starrables"""


    if dd.is_installed("stars"):

        star_object = StarObject()
        full_star_object = FullStarObject()
        unstar_object = UnstarObject()

        def disabled_fields(self, ar):
            s = super(Starrable, self).disabled_fields(ar)
            Star = rt.models.stars.Star
            user = ar.get_user()
            if not user.authenticated:
                s.add('unstar_object')
                s.add('star_object')
                s.add('full_star_object')
                return s
            master_star_qs = Star.for_obj(
                self, user=user, master__isnull=True)
            any_star_qs = Star.for_obj(self, user=user)
            if any_star_qs.count():
                s.add('star_object')
                if master_star_qs.count():
                    s.add('full_star_object')
                else:
                    s.add('unstar_object')
            else:
                s.add('full_star_object')
                s.add('unstar_object')
            # star = get_favourite(self, user)
            # if star is None:
            #     s.add('star_object')
            #     s.add('full_star_object')
            # else:
            return s

        def get_change_observers(self, ar=None):
            for o in super(Starrable, self).get_change_observers(ar):
                yield o
            users = set()
            for star in self.get_stars():
                if star.user not in users:
                    yield (star.user, star.user.mail_mode)
                    users.add(star.user)

        def get_stars(self):
            return rt.models.stars.Star.for_obj(self)

        def get_children_starrable(self):
            for model, fk, related in self.child_starrables:
                model = dd.resolve_model(model) if isinstance(model, string_types) else model
                for obj in model.objects.filter(**{fk: self}):
                    yield obj if related is None else getattr(obj, related)

        def add_child_stars(self, master, child,):
            """Add child stars to a master"""
            Star = rt.models.stars.Star
            for star in master.get_stars():
                try:
                    Star(owner=child, user=star.user, master=star).save()
                except IntegrityError:
                    #fastest way to solve this, the on_change methods are iiregularly called sometimes before create, sometimes not.
                    pass
