# -*- coding: UTF-8 -*-
# Copyright 2012-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from django.db import models
from django.utils.translation import pgettext_lazy
from django.utils.translation import get_language

from lino.api import dd, rt, _
from etgen.html import E, tostring_pretty
from lino.core.renderer import add_user_language

from lino.utils.mldbc.fields import LanguageField
from lino import mixins
from lino.mixins import Hierarchical, Sequenced
from lino.modlib.publisher.mixins import Publishable
from lino.modlib.memo.mixins import Previewable
from django.conf import settings
from .utils import render_node

#~ class PageType(dbutils.BabelNamed,mixins.PrintableType,outbox.MailableType):

    #~ templates_group = 'pages/Page'

    #~ class Meta:
        #~ verbose_name = _("Page Type")
        #~ verbose_name_plural = _("Page Types")

    #~ remark = models.TextField(verbose_name=_("Remark"),blank=True)

    #~ def __unicode__(self):
        #~ return self.name


#~ class PageTypes(dd.Table):
    #~ """
    #~ Displays all rows of :class:`PageType`.
    #~ """
    #~ model = 'pages.PageType'
    #~ column_names = 'name build_method template *'
    #~ order_by = ["name"]

    #~ detail_layout = """
    #~ id name
    #~ build_method template email_template attach_to_email
    #~ remark:60x5
    #~ pages.PagesByType
    #~ """


class Page(Hierarchical, Sequenced, Previewable, Publishable):

    class Meta:
        verbose_name = _("Node")
        verbose_name_plural = _("Nodes")
        unique_together = ["ref", "language"]

    publisher_location = "p"
    publisher_page_template = "pages/Node/default.pubpage.html"
    publisher_item_template = "pages/Node/default.pubitem.html"

    ref = models.CharField(
        _("Reference"), max_length=200, blank=True, null=True)
    language = LanguageField(default=models.NOT_PROVIDED, blank=True)
    title = dd.CharField(_("Title"), max_length=250, blank=True)
    # body = dd.BabelTextField(_("Body"), blank=True, format='plain')
    # raw_html = models.BooleanField(_("raw html"), default=False)

    @classmethod
    def lookup_page(cls, ref):
        try:
            return cls.objects.get(ref=ref, language=get_language())
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_dashboard_objects(cls, user):
        # print("20210114 get_dashboard_objects()", get_language())
        qs = Page.objects.filter(parent__isnull=True, language=get_language())
        for node in qs.order_by("seqno"):
            yield node

    def get_absolute_url(self, **kwargs):
        if self.ref:
            if self.ref != 'index':
                return dd.plugins.pages.build_plain_url(self.ref, **kwargs)
        return dd.plugins.pages.build_plain_url(**kwargs)

    def get_sidebar_caption(self):
        if self.title:
            return self.title
        if self.ref:
            return self.ref
        return str(self.id)

        #~ if self.ref or self.parent:
            #~ return self.ref
        #~ return unicode(_('Home'))

    def get_sidebar_item(self, request, other):
        kw = dict()
        add_user_language(kw, request)
        url = self.get_absolute_url(**kw)
        a = E.a(self.get_sidebar_caption(), href=url)
        if self == other:
            return E.li(a, **{'class':'active'})
        return E.li(a)

    def get_sidebar_html(self, request):
        items = []
        #~ loop over top-level nodes
        for n in Page.objects.filter(parent__isnull=True).order_by('seqno'):
            #~ items += [li for li in n.get_sidebar_items(request,self)]
            items.append(n.get_sidebar_item(request, self))
            if self.is_parented(n):
                children = []
                for ch in n.children.order_by('seqno'):
                    children.append(ch.get_sidebar_item(request, self))
                if len(children):
                    items.append(E.ul(*children, **{'class':'nav nav-list'}))

        e = E.ul(*items, **{'class':'nav nav-list'})
        return tostring_pretty(e)

    def get_sidebar_menu(self, request):
        qs = Page.objects.filter(parent__isnull=True, language=get_language())
        #~ qs = self.children.all()
        yield ('/', 'index', str(_('Home')))
            #~ yield ('/downloads/', 'downloads', 'Downloads')
        #~ yield ('/about', 'about', 'About')
        #~ if qs is not None:
        for obj in qs.order_by("seqno"):
            if obj.ref and obj.title:
                yield ('/' + obj.ref, obj.ref, obj.title)
            #~ else:
                #~ yield ('/','index',obj.title)


#~ class PageDetail(dd.FormLayout):
    #~ main = """
    #~ ref title type:25
    #~ project id user:10 language:8 build_time
    #~ left right
    #~ """
    #~ left = """
    # ~ # abstract:60x5
    #~ body:60x20
    #~ """
    #~ right="""
    #~ outbox.MailsByController
    #~ postings.PostingsByController
    #~ """
class PageDetail(dd.DetailLayout):
    main = """
    ref language parent seqno
    title
    body pages.PagesByParent
    """


class Pages(dd.Table):
    model = 'pages.Page'
    detail_layout = 'pages.PageDetail'
    column_names = "ref title *"
    #~ column_names = "ref language title user type project *"
    order_by = ["ref"]


#~ class MyPages(ByUser,Pages):
    #~ required = dict(user_groups='office')
    #~ column_names = "modified title type project *"
    #~ label = _("My pages")
    #~ order_by = ["-modified"]


class PagesByParent(Pages):
    master_key = 'parent'
    #~ column_names = "title user *"
    order_by = ["seqno"]
    column_names = "seqno title *"

#~ if settings.SITE.project_model:
    #~ class PagesByProject(Pages):
        #~ master_key = 'project'
        #~ column_names = "type title user *"
        #~ order_by = ["-modified"]
# def create_page(**kw):
#     #~ logger.info("20121219 create_page(%r)",kw['ref'])
#     return Page(**kw)
#
#
# def lookup(ref, *args, **kw):
#     return Page.get_by_ref(ref, *args, **kw)
#
# def get_all_pages():
#     return Page.objects.all()
