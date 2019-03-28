# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


"""
Datbase models for this plugin.

"""
from __future__ import unicode_literals
from builtins import str

from django.db import models
from django.conf import settings
from django.db.models import Q

from lino.api import dd, rt, _
from lino import mixins
from etgen.html import E, join_elems
from lino.modlib.comments.mixins import Commentable
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.notify.mixins import ChangeNotifier


class Group(mixins.BabelNamed, mixins.Referrable, ChangeNotifier,
            Commentable):

    class Meta:
        app_label = 'groups'
        abstract = dd.is_abstract_model(__name__, 'Group')
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    description = dd.RichTextField(
        _("Description"), blank=True, format='plain')


    @classmethod
    def setup_parameters(cls, fields):
        """Adds the :attr:`user` filter parameter field."""
        fields.setdefault(
            'user', dd.ForeignKey(
                'users.User', blank=True, null=True))
        super(Group, cls).setup_parameters(fields)

    def get_change_observers(self, ar=None):
        for x in super(Group, self).get_change_observers(ar):
            yield x
        for mbr in self.members.all():
            yield (mbr.user, mbr.user.mail_mode)
    
    @dd.displayfield(_("Recent comments"))
    def recent_comments(self, ar):
        if ar is None:
            return ''
        cls = rt.models.comments.CommentsByRFC
        sar = cls.request_from(
            ar, master_instance=self, limit=3)
        chunks = []
        for com in sar.sliced_data_iterator:
            chunks.append(ar.obj2html(com, str(com)))
        chunks.append("...")
        chunks = join_elems(chunks, ', ')

        sar = cls.insert_action.request_from(sar)
        if sar.get_permission():
            btn = sar.ar2button(None, _("Write comment"), icon_name=None)
            chunks.append(" ")
            chunks.append(btn)

        return E.div(*chunks)


class Groups(dd.Table):
    model = 'groups.Group'
    column_names = 'ref name *'
    order_by = ['ref']

    insert_layout = """
    ref name
    description
    """

    detail_layout = """
    ref:10 name:60 id
    description MembershipsByGroup 
    comments.CommentsByRFC
    """

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Groups, self).get_request_queryset(ar, **kwargs)
        pv = ar.param_values

        if pv.user:
            qs = qs.filter(
                Q(members__user=pv.user))
        return qs
            

    
class MyGroups(My, Groups):
    column_names = 'overview:10 recent_comments *'

    
    
@dd.python_2_unicode_compatible
class Membership(UserAuthored):

    class Meta:
        app_label = 'groups'
        abstract = dd.is_abstract_model(__name__, 'Membership')
        verbose_name = _("Group membership")
        verbose_name_plural = _("Group memberships")

    group = dd.ForeignKey('groups.Group', related_name="members")
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    def __str__(self):
        return _('{} in {}').format(self.user, self.group)


class Memberships(dd.Table):
    model = 'groups.Membership'


class MembershipsByGroup(Memberships):
    label = _("Memberships")
    master_key = 'group'
    column_names = "user remark workflow_buttons *"
    stay_in_grid = True
    display_mode = 'summary'

    @classmethod
    def get_table_summary(self, obj, ar):
        sar = self.request_from(ar, master_instance=obj)
        chunks = []
        
        for mbr in sar:
            chunks.append(ar.obj2html(mbr, str(mbr.user)))
        chunks = join_elems(chunks, ', ')

        # sar = self.insert_action.request_from(sar)
        # if sar.get_permission():
        #     btn = sar.ar2button(None, _("Add member"), icon_name=None)
        #     chunks.append(E.p((btn)))

        return E.div(*chunks)




class MembershipsByUser(Memberships):
    master_key = 'user'
    column_names = "group remark *"
    order_by = ['group__ref']


class AllMemberships(Memberships):
    required_roles = dd.login_required(dd.SiteAdmin)


