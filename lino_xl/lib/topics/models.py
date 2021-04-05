# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from etgen.html import E
from lino.api import dd, rt, _
from django.db import models

# from lino.core.utils import comma
from lino.core.gfks import gfk2lookup
from lino.mixins import BabelNamed
from lino.mixins.ref import StructuredReferrable
from lino.utils import join_elems
from lino.utils.instantiator import create_row
from lino.modlib.gfks.mixins import Controllable
from .roles import TopicsUser

class AddInterestField(dd.VirtualField):

    """An editable virtual field used for adding an interest to the
    object.

    """
    editable = True

    def __init__(self):
        return_type = dd.ForeignKey(
            'topics.Topic', verbose_name=_("Add interest"),
            blank=True, null=True)
        dd.VirtualField.__init__(self, return_type, None)

    def set_value_in_object(self, request, obj, value):
        # dd.logger.info("20170508 set_value_in_object(%s, %s)", obj, value)
        # if value is None:
        #     raise Exception("20170508")
        if value is not None:
            Interest = rt.models.topics.Interest
            if Interest.objects.filter(**gfk2lookup(
                    Interest.owner, obj, topic=value)).count() == 0:
                try:
                    create_row(Interest, topic=value, owner=obj)
                except Exception as e:
                    dd.logger.warning("20170508 ignoring %s", e)
        return obj

    def value_from_object(self, obj, ar):
        return None




# class TopicGroup(BabelNamed):

#     class Meta:
#         app_label = 'topics'
#         verbose_name = _("Topic group")
#         verbose_name_plural = _("Topic groups")
#         abstract = dd.is_abstract_model(__name__, 'TopicGroup')

#     description = models.TextField(_("Description"), blank=True)


# class TopicGroups(dd.Table):
#     model = 'topics.TopicGroup'
#     required_roles = dd.login_required(dd.SiteStaff)
#     order_by = ["id"]
#     # detail_layout = """
#     # id name
#     # description
#     # TopicsByGroup
#     # """


#
class Interest(Controllable):
    class Meta:
        app_label = 'topics'
        verbose_name = _("Interest")
        verbose_name_plural = _('Interests')

    allow_cascaded_delete = ["partner"]

    topic = dd.ForeignKey(
        'topics.Topic',
        related_name='interests_by_topic')

    remark = dd.RichTextField(
        _("Remark"), blank=True, format="plain")

    # def __str__(self):
    #     return str(self.topic)

    # used in lino_tera
    partner = dd.ForeignKey(
        dd.plugins.topics.partner_model,
        related_name='interests_by_partner', blank=True, null=True)



# dd.update_field(Interest, 'user', verbose_name=_("User"))

#
class Topic(StructuredReferrable, BabelNamed):

    ref_max_length = 5

    class Meta:
        app_label = 'topics'
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        abstract = dd.is_abstract_model(__name__, 'Topic')

    description_text = dd.BabelTextField(
        verbose_name=_("Long description"),
        blank=True, null=True)

    # topic_group = dd.ForeignKey(
    #     'topics.TopicGroup', blank=True, null=True)

    # def __str__(self):
    #     return "%s %s (%s)" % (
    #         self.last_name.upper(), self.first_name, self.pk)



class Topics(dd.Table):
    required_roles = dd.login_required(TopicsUser)
    model = 'topics.Topic'
    order_by = ["ref"]
    column_names = "ref name *"

    insert_layout = """
    ref
    name
    """

    detail_layout = """
    id ref name #topic_group
    description_text
    topics.InterestsByTopic
    """

class AllTopics(Topics):
    required_roles = dd.login_required(dd.SiteStaff)

# class TopicsByGroup(Topics):
#     master_key = 'topic_group'
#     required_roles = dd.login_required(dd.SiteStaff)


class Interests(dd.Table):
    required_roles = dd.login_required(TopicsUser)
    model = 'topics.Interest'
    column_names = "partner topic *"
    detail_layout = dd.DetailLayout("""
    partner
    topic owner
    remark
    """, window_size=(60, 15))

class AllInterests(Interests):
    required_roles = dd.login_required(dd.SiteStaff)


class InterestsByPartner(Interests):
    master_key = 'partner'
    order_by = ["topic"]
    column_names = 'topic *'
    display_mode = 'summary'
    stay_in_grid = True

    insert_layout = dd.InsertLayout("""
    topic
    remark
    """, window_size=(60, 10))

    # summary_sep = comma

    @classmethod
    def summary_row(cls, ar, obj, **kwargs):
        if ar is None:
            yield str(obj.topic)
        else:
            yield ar.obj2html(obj, str(obj.topic))


class InterestsByController(Interests):
    master_key = 'owner'
    order_by = ["topic"]
    column_names = 'topic *'
    stay_in_grid = True
    display_mode = 'summary'
    insert_layout = dd.InsertLayout("""
    topic partner
    remark
    """, window_size=(60, 10))

    # summary_sep = comma

    @classmethod
    def summary_row(cls, ar, obj, **kwargs):
        if ar is None:
            yield str(obj.topic)
        else:
            yield ar.obj2html(obj, str(obj.topic))



class InterestsByTopic(Interests):
    master_key = 'topic'
    order_by = ["id"]
    column_names = 'partner owner *'
