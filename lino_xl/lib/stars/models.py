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

class Star(UserAuthored, Controllable):
    """Represents the fact that a given database object is starred by a
    given User.

    .. attribute:: owner

        The starred database object

    .. attribute:: user

        The starring user (pointer to :class:lino.modlib.users.models.User`

    .. attribute:: nickname

    """

    # controller_is_optional = False

    nickname = models.CharField(_("Nickname"), max_length=50, blank=True)

    class Meta:
        app_label = 'stars'
        verbose_name = _("Star")
        verbose_name_plural = _("Stars")

    @classmethod
    def for_obj(cls, obj, **kwargs):
        """Return a queryset of :class:`Star` instances for the given database
        object.

        """
        return cls.objects.filter(**gfk2lookup(cls.owner, obj, **kwargs))

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

