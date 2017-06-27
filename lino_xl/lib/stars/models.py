# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Database models for `lino_xl.lib.stars`.

"""


from django.db import models
from django.contrib.contenttypes.models import ContentType
from lino.api import dd, rt, _
from lino.core.gfks import gfk2lookup
from lino.modlib.gfks.mixins import Controllable
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.office.roles import OfficeUser
# from lino.core.requests import BaseRequest
from six import string_types

from lino.core.gfks import gfk2lookup
from django.utils.translation import string_concat

from lino.modlib.gfks.fields import GenericForeignKey, GenericForeignKeyIdField

class Star(UserAuthored, Controllable):
    """Represents the fact that a given database object is starred by a
    given User.

    .. attribute:: owner

        The starred database object

    .. attribute:: user

        The starring user (pointer to :class:lino.modlib.users.models.User`

    .. attribute:: nickname


    .. attribute:: master

        The starred object that caused this stared object

    """

    # controller_is_optional = False
    allow_cascaded_delete = 'master'
    allow_cascaded_copy = 'master'

    nickname = models.CharField(_("Nickname"), max_length=50, blank=True)

    class Meta:
        app_label = 'stars'
        verbose_name = _("Star")
        verbose_name_plural = _("Stars")
        unique_together = ('user', 'owner_id', 'owner_type', 'master',)
        
    @classmethod
    def for_obj(cls, obj, **kwargs):
        """Return a queryset of :class:`Star` instances for the given database
        object.

        """
        return cls.objects.filter(**gfk2lookup(cls.owner, obj, **kwargs))

    @classmethod
    def for_obj_and_master(cls, obj, master, **kwargs):
        kwargs = gfk2lookup(cls.owner, obj, **kwargs)
        kwargs = gfk2lookup(cls.master, master, **kwargs)
        return cls.objects.filter(**gfk2lookup(cls.owner, obj, **kwargs))

    @classmethod
    def for_master(cls, master, **kwargs):
        return cls.objects.filter(**gfk2lookup(cls.master, master, **kwargs))

    @classmethod
    def for_model(cls, model, **kwargs):
        """Return a queryset of :class:`Star` instances for the given database
        model.
        """
        if isinstance(model, string_types):
            model = dd.resolve_model(model)
        ct = ContentType.objects.get_for_model(model)
        kwargs[cls.owner.ct_field]= ct
        return cls.objects.filter(**kwargs)

    #
    # master_label = _("Master object")
    #
    #
    # master_type = dd.ForeignKey(
    #     ContentType,
    #     editable=True,
    #     blank=True, null=True,
    #     verbose_name=string_concat(master_label, ' ', _('(type)')),
    #     related_name='stars_by_master')
    # master_id = GenericForeignKeyIdField(
    #     master_type,
    #     editable=True,
    #     blank=True, null=True,
    #     verbose_name=string_concat(master_label, ' ', _('(object)')))
    # master = GenericForeignKey(
    #     'master_type', 'master_id',
    #     verbose_name=master_label
    # )
    master = dd.ForeignKey('self',
                           verbose_name=_("Master_Star"),
                           blank=True, null=True,
                           related_name=_("children_stars"),
                           # on_delete=models.CASCADE,
                           )
    @classmethod
    def create_star(cls, obj, ar):
        # todo: Fix in extjs6, user is always user not subuser
        star = cls(owner=obj, user=ar.get_user())
        star.save()
        star.create_children(obj, ar)

    def create_children(self, obj, ar):
        for child in self.owner.get_children_starrable(ar):
            Star(owner=child, user=ar.get_user(), master=self).save()

    def after_ui_create(self, ar):
        #Needed for when creating Tickets for other Users on a table-view.
        self.create_children(self.owner, ar)
        super(Star, self).after_ui_create(ar)

dd.update_field(Star, 'user', verbose_name=_("User"), blank=False, null=False)
dd.update_field(Star, 'owner', verbose_name=_("Starred object"))

Star.update_controller_field(blank=False, null=False)


class Stars(dd.Table):
    model = 'stars.Star'
    column_names = "id owner user nickname *"
    parameters = dict(
                type=dd.ForeignKey(ContentType, blank=False, null=False)
    )
    # params_layout = """"""

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Stars, self).get_request_queryset(ar)
        pv = ar.param_values
        if pv['type']:
            qs=qs.filter(owner_type=pv['type'])
        return qs


class AllStars(Stars):
    required_roles = dd.login_required(dd.SiteStaff)

class MyStars(My, Stars):
    required_roles = dd.login_required(OfficeUser)
    column_names = "owner nickname owner_type *"
    order_by = ['nickname', 'id']


class StarsByController(Stars):
    label = _("Starred by")
    master_key = 'owner'
    column_names = "user *"


from lino.utils.xmlgen.html import E
from lino.utils import join_elems


def welcome_messages(ar):
    """Yield a message "Your stars are X, Y, ..." for the welcome page.

    This message mentions all starred objects of the requesting user
    and whose :attr:`nickname <Star.nickname>` is not empty.

    """
    Star = rt.modules.stars.Star
    qs = Star.objects.filter(user=ar.get_user()).exclude(nickname='')
    if qs.count() > 0:
        chunks = [unicode(_("Your stars are "))]
        chunks += join_elems([
            ar.obj2html(obj.owner, obj.nickname or unicode(obj.owner))
            for obj in qs])
        chunks.append('.')
        yield E.span(*chunks)


dd.add_welcome_handler(welcome_messages)

