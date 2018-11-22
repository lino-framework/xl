# -*- coding: UTF-8 -*-
# Copyright 2009-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

from django import http
from django.views.generic import View

from lino.api import rt



class PagesIndex(View):

    def get(self, request, ref='index'):
        if not ref:
            ref = 'index'

        #~ print 20121220, ref
        obj = rt.models.pages.lookup(ref, None)
        if obj is None:
            raise http.Http404("Unknown page %r" % ref)
        html = rt.models.pages.render_node(request, obj)
        return http.HttpResponse(html)
