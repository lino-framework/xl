# -*- coding: UTF-8 -*-
# Copyright 2011-2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Database models for :mod:`lino_xl.lib.topics`.

"""


from lino.api import dd, _
from django.db import models

from lino.mixins import BabelNamed, Referrable


class TopicGroup(BabelNamed):
    """A **group of topics** is the default way to group topics."""

    class Meta:
        app_label = 'topics'
        verbose_name = _("Topic group")
        verbose_name_plural = _("Topic groups")
        abstract = dd.is_abstract_model(__name__, 'TopicGroup')

    description = models.TextField(_("Description"), blank=True)


class TopicGroups(dd.Table):
    model = 'topics.TopicGroup'
    required_roles = dd.required(dd.SiteStaff)
    order_by = ["id"]
    detail_layout = """
    id name
    description
    TopicsByGroup
    """


class Interest(dd.Model):
    """An **interest** is the fact that a given partner is interested in a
given topic.

    """
    class Meta:
        app_label = 'topics'
        verbose_name = _("Interest")
        verbose_name_plural = _('Interests')

    topic = dd.ForeignKey(
        'topics.Topic',
        related_name='interests_by_topic')

    partner = dd.ForeignKey(
        dd.plugins.topics.partner_model,
        related_name='interests_by_partner')


# dd.update_field(Interest, 'user', verbose_name=_("User"))


class Topic(BabelNamed, Referrable):
    """A topic is something somebody can be interested in.

    .. attribute:: ref
    .. attribute:: description
    

    """

    class Meta:
        app_label = 'topics'
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        abstract = dd.is_abstract_model(__name__, 'Topic')

    description = dd.BabelTextField(
        verbose_name=_("Long description"),
        blank=True, null=True)

    topic_group = dd.ForeignKey(
        'topics.TopicGroup', blank=True, null=True)


class Topics(dd.Table):
    model = 'topics.Topic'
    order_by = ["id"]
    column_names = "ref name topic_group *"

    insert_layout = """
    topic_group
    name
    """

    detail_layout = """
    id ref name topic_group
    description
    topics.InterestsByTopic
    """

class AllTopics(Topics):
    required_roles = dd.required(dd.SiteStaff)

class TopicsByGroup(Topics):
    master_key = 'topic_group'
    required_roles = dd.required(dd.SiteStaff)


class Interests(dd.Table):
    model = 'topics.Interest'
    column_names = "partner topic *"

class AllInterests(Interests):
    required_roles = dd.required(dd.SiteStaff)
    
class InterestsByPartner(Interests):
    master_key = 'partner'
    order_by = ["topic"]
    column_names = 'topic *'


class InterestsByTopic(Interests):
    master_key = 'topic'
    order_by = ["partner"]
    column_names = 'partner *'


