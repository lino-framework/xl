# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Database models for :mod:`lino_xl.lib.topics`.

"""
from __future__ import unicode_literals

import six
# from builtins import str

from lino.api import dd, rt, _
from django.db import models

from lino.mixins import BabelNamed, Referrable
from lino.utils import join_elems
from lino.utils.instantiator import create_row
from etgen.html import E
from lino.modlib.gfks.mixins import Controllable
from lino.core.gfks import gfk2lookup

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




class TopicGroup(BabelNamed):
    """Currently not used. """

    class Meta:
        app_label = 'topics'
        verbose_name = _("Topic group")
        verbose_name_plural = _("Topic groups")
        abstract = dd.is_abstract_model(__name__, 'TopicGroup')

    description = models.TextField(_("Description"), blank=True)


class TopicGroups(dd.Table):
    model = 'topics.TopicGroup'
    required_roles = dd.login_required(dd.SiteStaff)
    order_by = ["id"]
    detail_layout = """
    id name
    description
    TopicsByGroup
    """


class Interest(Controllable):
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
    
    remark = dd.RichTextField(
        _("Remark"), blank=True, format="plain")
    
    # deprecated field just for backwards compatibility:
    partner = dd.ForeignKey(
        dd.plugins.topics.partner_model,
        related_name='interests_by_partner', blank=True, null=True)



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
    required_roles = dd.login_required(dd.SiteStaff)

class TopicsByGroup(Topics):
    master_key = 'topic_group'
    required_roles = dd.login_required(dd.SiteStaff)


class Interests(dd.Table):
    model = 'topics.Interest'
    column_names = "partner topic *"

class AllInterests(Interests):
    required_roles = dd.login_required(dd.SiteStaff)
    
class InterestsByPartner(Interests):
    master_key = 'partner'
    order_by = ["topic"]
    column_names = 'topic *'


class InterestsByController(Interests):
    master_key = 'owner'
    order_by = ["topic"]
    column_names = 'topic *'
    stay_in_grid = True
    display_mode = 'summary'
    # detail_layout = dd.DetailLayout("""
    # owner_type
    # owner_id
    # topic
    # remark
    # """, window_size=(60, 15))
    
    @classmethod
    def get_table_summary(self, obj, ar):
        """Implements :meth:`summary view
        <lino.core.actors.Actor.get_table_summary>`.

        """
        sar = self.request_from(ar, master_instance=obj)
        # tags = [str(c.topic) for c in sar]
        tags = [six.text_type(c.topic) for c in sar]
        # tags = [c.obj2href(ar) for c in sar]
        # chunks = join_elems(tags, sep=', ')
        # iar = self.insert_action.request_from(sar)
        # if iar.get_permission():
        #     chunks.append(' ')
        #     chunks.append(iar.ar2button())
        # return ar.html_text(E.p(*chunks))
        return ar.html_text(E.p(', '.join(tags)))




class InterestsByTopic(Interests):
    master_key = 'topic'
    order_by = ["id"]
    column_names = 'owner *'


