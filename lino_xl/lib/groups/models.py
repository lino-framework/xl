# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from builtins import str

from django.db import models
from django.conf import settings
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericRelation

from lino.api import dd, rt, _
from lino import mixins
from etgen.html import E, join_elems
from lino.modlib.comments.mixins import Commentable, PrivateCommentsReader
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

    comments = GenericRelation('comments.Comment',
        content_type_field='owner_type', object_id_field='owner_id',
        related_query_name="group")


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

    @classmethod
    def get_comments_filter(cls, user):
        if user.user_type.has_required_roles([PrivateCommentsReader]):
            return None
        if user.is_anonymous:
            return super(Group, cls).get_comments_filter(user)
        flt = Q(group__members__user=user)
        flt |= Q(user=user) | Q(private=False)
        return flt


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




class Membership(UserAuthored):

    class Meta:
        app_label = 'groups'
        abstract = dd.is_abstract_model(__name__, 'Membership')
        verbose_name = _("Group membership")
        verbose_name_plural = _("Group memberships")

    group = dd.ForeignKey('groups.Group', related_name="members")
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    allow_cascaded_delete = ['site', 'user','group']

    def __str__(self):
        return _('{} in {}').format(self.user, self.group)

dd.update_field(Membership, "user", verbose_name=_("User"))

class Memberships(dd.Table):
    model = 'groups.Membership'
    insert_layout = dd.InsertLayout("""
    user
    group
    remark
    """, window_size=(60, 'auto'))

    detail_layout = dd.DetailLayout("""
    user
    group
    remark
    """, window_size=(60, 'auto'))



class MembershipsByGroup(Memberships):
    label = _("Memberships")
    master_key = 'group'
    column_names = "user remark workflow_buttons *"
    stay_in_grid = True
    display_mode = 'summary'

    # summary_sep = comma

    @classmethod
    def summary_row(cls, ar, obj, **kwargs):
        if ar is None:
            yield str(obj.user)
        else:
            yield ar.obj2html(obj, str(obj.user))

    @classmethod
    def unused_get_table_summary(self, obj, ar):
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
    display_mode = 'summary'


class AllMemberships(Memberships):
    required_roles = dd.login_required(dd.SiteAdmin)
