# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

#~ print 20121219, __file__


from django.conf import settings

from lino.api import dd

from lino.utils.restify import restify
from lino.utils.restify import doc2rst

def render_node(request, node, template_name='pages/node.html', **context):
    context.update(node=node)
    heading = dd.babelattr(node, 'title', '')
    if settings.SITE.title is None:
        title = settings.SITE.verbose_name
    else:
        title = settings.SITE.title

    if heading:
        context.update(heading=heading)
        context.update(title=heading + ' &middot; ' + title)
    else:
        context.update(heading=title)
        context.update(title=title)
    body = dd.babelattr(node, 'body', '')
    if not node.raw_html:
        body = restify(doc2rst(body))
    # dd.logger.info("20121227 render_node %s -> body is %s",node,body)
    context.update(body=body)
    # return web.render_from_request(request, template_name, **context)
    return dd.plugins.jinja.render_from_request(
        request, template_name, **context)


