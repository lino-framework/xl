# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Database models for `lino_xl.lib.stars`.

"""
from builtins import str

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

# from lino.modlib.gfks.fields import GenericForeignKey, GenericForeignKeyIdField

@dd.python_2_unicode_compatible
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
    allow_cascaded_delete = 'master owner'
    allow_cascaded_copy = 'master' #owner does not work ticket #1948

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

    @classmethod
    def for_master_model(cls, model, **kwargs):
        """Return a queryset of master :class:`Star` instances for the given database
        model.
        """
        if isinstance(model, string_types):
            model = dd.resolve_model(model)
        ct = ContentType.objects.get_for_model(model)
        kwargs["master__" + cls.owner.ct_field] = ct
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
        star.create_children(ar)

    def yield_children(self, user):
        for child in self.owner.get_children_starrable():
            yield Star(owner=child, user=user, master=self)


    def create_children(self, ar):
        for child in self.yield_children(ar.get_user()):
            child.save()

    @classmethod
    def get_parent_star_from_model(cls, master_model, child, ar):
        # lookup a parent star when all you know is the model of the parent
        kw = gfk2lookup(Star.owner, child, user=ar.get_user())
        return cls.for_master_model(master_model, **kw)

    def after_ui_create(self, ar):
        #Needed for when creating Tickets for other Users on a table-view.
        self.create_children(ar)
        super(Star, self).after_ui_create(ar)

    @dd.displayfield(_("Stared Because"))
    def master_owner(self, ar):
        if ar is None: return None
        return ar.obj2html(self.master.owner) if self.master is not None else ""

    def __str__(self):
        return _("{} starring {}").format(self.user, self.owner)

dd.update_field(Star, 'user', verbose_name=_("User"), blank=False, null=False)
dd.update_field(Star, 'owner', verbose_name=_("Starred object"))

Star.update_controller_field(blank=False, null=False)


class Stars(dd.Table):
    model = 'stars.Star'
    column_names = "id owner user nickname master_owner *"
    parameters = dict(
                type=dd.ForeignKey(ContentType, blank=True, null=True),
                inherited_stars=dd.YesNo.field(_("inherited stars"), blank=True, null=True)
    )
    # params_layout = """"""

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Stars, self).get_request_queryset(ar, **kwargs)
        pv = ar.param_values
        if pv['type']:
            qs = qs.filter(owner_type=pv['type'])
        if pv['inherited_stars'] is dd.YesNo.no:
            qs = qs.filter(master__isnull=True)
        elif pv['inherited_stars'] is dd.YesNo.yes:
            qs = qs.filter(master__isnull=False)

        return qs


class AllStars(Stars):
    required_roles = dd.login_required(dd.SiteStaff)

class MyStars(My, Stars):
    required_roles = dd.login_required(OfficeUser)
    column_names = "owner nickname owner_type master_owner *"
    order_by = ['nickname', 'id']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyStars, self).param_defaults(ar, **kw)
        kw.update(inherited_stars=dd.YesNo.no)
        return kw

class StarsByController(Stars):
    label = _("Starred by")
    master_key = 'owner'
    column_names = "user *"
    display_mode = 'summary'

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(StarsByController, self).param_defaults(ar, **kw)
        kw.update(inherited_stars=dd.YesNo.no)
        return kw

class AllStarsByController(Stars):
    label = _("Starred by")
    master_key = 'owner'
    column_names = "user master_owner *"


from etgen.html import E, join_elems


def welcome_messages(ar):
    """Yield a message "Your stars are X, Y, ..." for the welcome page.

    This message mentions all starred objects of the requesting user
    and whose :attr:`nickname <Star.nickname>` is not empty.

    """
    Star = rt.models.stars.Star
    qs = Star.objects.filter(user=ar.get_user()).exclude(nickname='')
    if qs.count() > 0:
        chunks = [str(_("Your stars are "))]
        chunks += join_elems([
            ar.obj2html(obj.owner, obj.nickname or unicode(obj.owner))
            for obj in qs])
        chunks.append('.')
        yield E.span(*chunks)


dd.add_welcome_handler(welcome_messages)


def Create_Stars_From_Scratch():
    """ Function to re-create logical stars after updateing Jane with the new Star model"""
    for Ticket in rt.models.tickets.Ticket.objects.all():
        Ticket.after_ui_create(None) # Sets auther enduser and asigned stars
    for comment in rt.models.comments.Comment.objects.all():
        if isinstance(comment.owner, rt.models.tickets.Ticket):
            Ticket.add_change_watcher(comment.user)
    for session in rt.models.working.Session.objects.all():
        session.ticket.add_change_watcher(session.user)

