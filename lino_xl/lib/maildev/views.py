# Modified copy of https://github.com/kyokenn/djradicale/blob/master/djradicale/views.py
# The original is Copyright (C) 2014 Okami, okami@fuzetsu.info and published using GPL.
# Our modifications are Copyright 2017 Luc Saffre, Tonis Piip

import base64
import copy

from django.conf import settings
# from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView, View
from django.utils.decorators import method_decorator

from radicale import Application


class ApplicationResponse(HttpResponse):
    def start_response(self, status, headers):
        self.status_code = int(status.split(' ')[0])
        for k, v in dict(headers).items():
            self[k] = v


class DjRadicaleView(Application, View):
    http_method_names = [
        'delete',
        'get',
        'head',
        'mkcalendar',
        'mkcol',
        'move',
        'options',
        'propfind',
        'proppatch',
        'put',
        'report',
    ]

    def __init__(self, **kwargs):
        super(DjRadicaleView, self).__init__()
        super(View, self).__init__(**kwargs)

    def do_HEAD(self, environ, read_collections, write_collections, content,
                user):
        """Manage HEAD request."""
        status, headers, answer = self.do_GET(
            environ, read_collections, write_collections, content, user)
        return status, headers, None

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.method.lower() in self.http_method_names:
            return self.http_method_not_allowed(request, *args, **kwargs)
        print "20170403 1z"
        response = ApplicationResponse()
        answer = self(request.META, response.start_response)
        print "20170403"
        for i in answer:
            response.write(i)
        return response


class WellKnownView(DjRadicaleView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # do not authentificate yet, just get the username
        if 'HTTP_AUTHORIZATION' in self.request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2:
                if auth[0].lower() == 'basic':
                    user, password = base64.b64decode(
                        auth[1]).decode().split(':')
                    if kwargs.get('type') == 'carddav':
                        url = '%s/addressbook.vcf/' % user
                    else:
                        url = '%s/calendar.ics/' % user
                    request.META['PATH_INFO'] = reverse(
                        'djradicale:application', kwargs={'url': url})
        return super(WellKnownView, self).dispatch(request, *args, **kwargs)
